from otree.api import *
import pandas as pd
import datetime as dt
import time
import os

now = dt.now()
filename_number = now.strftime("prisoner_result_%Y-%m-%d_%H-%M-%S")

df = pd.DataFrame(columns=['session', 'player',
                  'round', 'cooperate', 'payoff', 'start_time', 'choice_time', 'time_out_choice'])


doc = """
This is a 20-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""

# 環境変数のセッティングをしてください。
# OTREE_PRODUCTION=1
# export OTREE_PRODUCTION


class C(BaseConstants):
    NAME_IN_URL = 'prisoner_copy_copy_prc'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 22
    ENDOWMENT = cu(100)  # 初期保有
    # 利得は以下を満たすようにしてください。
    # PAYOFF_A>B>C>D 2A>B+C
    PAYOFF_A = 30  # 利得(D,C)
    PAYOFF_B = 10  # 利得(C,C)
    PAYOFF_C = -10  # 利得(D,D)
    PAYOFF_D = -20  # 利得(C,D)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):  # 記録したいものを書く
    cooperate = models.BooleanField()  # 協力or非協力 bool値,T:協力,F:非協力
    payoff = models.IntegerField()  # 獲得した利得


class Player(BasePlayer):
    timeout_happened = models.BooleanField(initial=False)
    choice_timestamp = models.FloatField()
    start_timestamp = models.FloatField()
    time_out_choice = models.BooleanField()
    add_point = models.IntegerField()
    cooperate = models.BooleanField(
        choices=[[True, 'Option I'], [False, 'Option J']],
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
    payoff_matrix = {
        (False, True): (C.PAYOFF_A, C.PAYOFF_D),
        (True, True): (C.PAYOFF_B, C.PAYOFF_B),
        (False, False): (C.PAYOFF_C, C.PAYOFF_C),
        (True, False): (C.PAYOFF_D, C.PAYOFF_A),
    }
    other = other_player(player)
    score_matrix = payoff_matrix[(
        player.cooperate, other.cooperate)]  # スコア２人分の配列

    if player.time_out_choice and other.time_out_choice:
        if player.round_number == 1 or player.round_number == 3:
            player.payoff = C.ENDOWMENT  # 自分の配列
            player.add_point = 0
            other.payoff = C.ENDOWMENT  # 相手の配列
            other.add_point = 0
        else:
            player.payoff = prev_player(player).payoff
            player.add_point = 0
            other.payoff = prev_player(other).payoff
            other.add_point = 0

    elif player.time_out_choice:
        if player.round_number == 1 or player.round_number == 3:
            player.payoff = C.ENDOWMENT  # 自分の配列
            player.add_point = 0
            other.payoff = C.ENDOWMENT  # 相手の配列
            other.add_point = 0
        else:
            player.payoff = prev_player(player).payoff
            player.add_point = 0
            other.payoff = prev_player(other).payoff
            other.add_point = 0
    elif other.time_out_choice:
        if player.round_number == 1 or player.round_number == 3:
            player.payoff = C.ENDOWMENT  # 自分の配列
            player.add_point = 0
            other.payoff = C.ENDOWMENT  # 相手の配列
            other.add_point = 0
        else:
            player.payoff = prev_player(player).payoff
            player.add_point = 0
            other.payoff = prev_player(other).payoff
            other.add_point = 0
    else:
        if player.round_number == 1 or player.round_number == 3:
            player.payoff = C.ENDOWMENT+score_matrix[0]  # 自分の配列
            player.add_point = score_matrix[0]
            other.payoff = C.ENDOWMENT+score_matrix[1]  # 相手の配列
            other.add_point = score_matrix[1]
        else:
            player.payoff = prev_player(player).payoff+score_matrix[0]  # 自分の配列
            player.add_point = score_matrix[0]
            other.payoff = prev_player(other).payoff+score_matrix[1]  # 相手の配列
            other.add_point = score_matrix[1]

    df.loc[len(df)] = [player.session.code, player.id_in_subsession,
                       player.round_number, player.cooperate, player.payoff, player.start_timestamp, player.choice_timestamp, player.time_out_choice]

    if (player.round_number == C.NUM_ROUNDS):
        # 奇数行と偶数行を分けます
        odd_rows = df[df.index % 2 == 0]
        even_rows = df[df.index % 2 == 1]

        # 奇数行のカラム名を変更します
        odd_rows.columns = [f'{col}_p1' for col in odd_rows.columns]

        # 偶数行のカラム名を変更します
        even_rows.columns = [f'{col}_p2' for col in even_rows.columns]

        # 奇数行と偶数行を水平に結合します
        result = pd.concat([odd_rows.reset_index(drop=True), even_rows.reset_index(drop=True)], axis=1)

        # カラムの順番を入れ替えたい順番に指定
        new_column_order = [
            'session_p1',
            'session_p2',
            'round_p1',
            'round_p2',
            'player_p1',
            'player_p2',
            'cooperate_p1',
            'cooperate_p2',
            'payoff_p1',
            'payoff_p2',
            'start_time_p1',
            'start_time_p2',
            'choice_time_p1',
            'choice_time_p2',
            'time_out_choice_p1',
            'time_out_choice_p2',
        ]

        # カラムの順番を変更、不要なカラムを削除
        result = result[new_column_order]

        # 結果をCSVファイルとして保存します
        os.makedirs("output/prisoner_result", exist_ok=True)
        result.to_csv(f'output/prisoner_result/prisoner_result_{filename_number}.csv', encoding='utf-8-sig', index=False)


# PAGES
# participant_wait_page
class Wait_Page(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Introduction(Page):
    timer_text = "次の画面になるまでお待ちください。"

    def get_timeout_seconds(player: Player):
        # プレイヤーごとに異なるタイムアウト秒数を計算して返す
        if player.round_number == 1:
            return 3
        else:
            return 3

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
        other = other_player(player)
        if not timeout_happened:
            player.time_out_choice = False
        else:
            player.time_out_choice = True

        # Calculate the remaining time in seconds
        remaining_time = Decision.timeout_seconds - (time.time() - player.start_timestamp)

        if remaining_time > 0:
            # Sleep for the remaining time
            time.sleep(remaining_time)
        player.choice_timestamp = time.time()


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


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

        NUM_ROUNDS = C.NUM_ROUNDS
        other = other_player(player)
        return dict(
            NUM_ROUNDS=NUM_ROUNDS,
            other=other,
            opponent=other,
            player_addpoint=player.add_point,
            other_addpoint=other.add_point,
            playertime_out_choice=player.time_out_choice,
            othertime_out_choice=other.time_out_choice,
            round_number=player.round_number,
            same_choice=player.cooperate == other.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=other.field_display('cooperate'),
        )

    def before_next_page(player: Player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            os._exit(0)


page_sequence = [Wait_Page, Introduction, Decision, ResultsWaitPage, Results]
