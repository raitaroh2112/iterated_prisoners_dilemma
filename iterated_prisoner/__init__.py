from otree.api import *
import pandas as pd
import datetime
import time
import os
from .file_writer import write_to_csv

doc = """
2人対戦の繰り返し囚人のジレンマゲームです。
"""

now = datetime.datetime.now()
filename_number = now.strftime("prisoner_result_%Y-%m-%d_%H-%M-%S")

df = pd.DataFrame(columns=['session', 'player', 'round', 'cooperate', 'payoff', 'start_choice_time', 'end_choice_time', 'time_out_choice'])


class C(BaseConstants): # 定数の設定(パラメータはお好みで)
    NAME_IN_URL = 'iterated_prisoner'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    ENDOWMENT = cu(100)  # 初期保有
    # PAYOFF_A>B>C>D 2A>B+C
    PAYOFF_A = 5  # 利得(D,C)
    PAYOFF_B = 3  # 利得(C,C)
    PAYOFF_C = 0  # 利得(D,D)
    PAYOFF_D = -1  # 利得(C,D)


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.group_randomly()
            for g in self.get_groups():
                for p in g.get_players():
                    if p.id_in_group % 2 == 0:
                        p.participant.vars['type'] = 'BLUE'
                    else:
                        p.participant.vars['type'] = 'GREEN'
                    p.type = p.participant.vars['type']
        else:
            self.group_like_round(1)


class Group(BaseGroup):  
    payoff = models.IntegerField()  


class Player(BasePlayer):
    timeout_happened = models.BooleanField(initial=False)
    time_out_choice = models.BooleanField(initial=False)
    choice_timestamp = models.FloatField()
    start_timestamp = models.FloatField()
    add_point = models.IntegerField()
    cooperate = models.IntegerField(
        default=0,  # cooperateフィールドの初期値を0に設定
        choices=[[0, '未入力'], [1, 'Option I'], [2, 'Option J']], 
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )

# FUNCTIONS


def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)


def other_player(player: Player):
    return player.get_others_in_group()[0]


def prev_player(player: Player):

    if player.round_number > 1:
        return player.in_round(player.round_number - 1)


def display_score(player: Player):
    if player.round_number == 1 or player.round_number == 3:
        return C.ENDOWMENT
    else:
        return prev_player(player).payoff


def set_payoff(player: Player):

    if player.cooperate == 0 or other_player(player).cooperate == 0:
        player.cooperate = 0 # 未入力の場合は、前の点数に+0として設定する

        # 前の点数に+0として設定する
        if player.round_number == 1 or player.round_number == 3:
            player.payoff = C.ENDOWMENT
            player.add_point = 0
            other = other_player(player)
            other.payoff = C.ENDOWMENT
            other.add_point = 0
        else:
            player.payoff = prev_player(player).payoff
            player.add_point = 0
            other = other_player(player)
            other.payoff = prev_player(other).payoff
            other.add_point = 0
    else:
        payoff_matrix = {
            (2, 1): (C.PAYOFF_A, C.PAYOFF_D),
            (1, 1): (C.PAYOFF_B, C.PAYOFF_B),
            (2, 2): (C.PAYOFF_C, C.PAYOFF_C),
            (1, 2): (C.PAYOFF_D, C.PAYOFF_A),
        }
        other = other_player(player)
        score_matrix = payoff_matrix[(
            player.cooperate, other.cooperate)]  # スコア２人分の配列

        if player.round_number == 1 or player.round_number == 3:
            player.payoff = C.ENDOWMENT+score_matrix[0]  
            player.add_point = score_matrix[0]
            other.payoff = C.ENDOWMENT+score_matrix[1]  
            other.add_point = score_matrix[1]
        else:
            player.payoff = prev_player(player).payoff+score_matrix[0]  
            player.add_point = score_matrix[0]
            other.payoff = prev_player(other).payoff+score_matrix[1] 
            other.add_point = score_matrix[1]

    df.loc[len(df)] = [player.session.code, player.id_in_subsession,
                       player.round_number, player.cooperate, player.payoff, player.start_timestamp, player.choice_timestamp, player.time_out_choice]

    if (player.round_number == C.NUM_ROUNDS):
        # ファイルに書き込み
        # 結果をCSVファイルとして保存します
        write_to_csv(df, filename_number)


# PAGES
# participant_wait_page
class Wait_Page(WaitPage):
    pass


class Introduction(Page):
    timer_text = "次の画面になるまでお待ちください。"

    def get_timeout_seconds(player: Player):
        # 最初のラウンドのみ、10秒のタイムアウトを設定
        if player.round_number == 1:
            return 10
        else:
            return 5

    @staticmethod
    def vars_for_template(player: Player):
        other = other_player(player)
        point_player = display_score(player)
        point_other = display_score(other)
        return dict(
            other=other,
            round_number=player.round_number,
            point_player=point_player,
            point_other=point_other,

        )

    def before_next_page(player: Player, timeout_happened):
        player.start_timestamp = time.time()


class Wait_Page_Decision(WaitPage):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.start_timestamp = time.time()


class Decision(Page):
    timeout_seconds = 20
    timer_text = "制限時間内に選択してください"
    form_model = 'player'
    form_fields = ['cooperate']

    @staticmethod
    def vars_for_template(player: Player):
        other = other_player(player)
        point_player = display_score(player)
        point_other = display_score(other)

        return dict(
            other=other,
            round_number=player.round_number,
            point_player=point_player,
            point_other=point_other,


        )

    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened:
            player.time_out_choice = False
        else:
            player.time_out_choice = True
            
        player.choice_timestamp = time.time()


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    timeout_seconds = 20


class Results(Page):
    timer_text = " 次の画面になるまでお待ちください。"

    def get_timeout_seconds(player: Player):
        # プレイヤーごとに異なるタイムアウト秒数を計算して返す
        if player.round_number == C.NUM_ROUNDS:
            return 120
        else:
            return 10

    @staticmethod
    def vars_for_template(player: Player):
        if player.cooperate == 0 or other_player(player).cooperate == 0:
            not_entered_message = "制限時間以内に操作が終わらなかったため、無効試合となります。"
        else:
            not_entered_message = None

        NUM_ROUNDS = C.NUM_ROUNDS
        other = other_player(player)
        return dict(
            NUM_ROUNDS=NUM_ROUNDS,
            other=other,
            opponent=other,
            player_addpoint=player.add_point,
            other_addpoint=other.add_point,
            round_number=player.round_number,
            my_decision=player.field_display('cooperate'),
            opponent_decision=other.field_display('cooperate'),
            not_entered_message=not_entered_message,
        )

    def before_next_page(player: Player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            pass


page_sequence = [Wait_Page, Introduction,
                 Wait_Page_Decision, Decision,  ResultsWaitPage, Results]
