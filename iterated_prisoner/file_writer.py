import os
import pandas as pd

def write_to_csv(df, filename_number):
    # 出力をcsvに保存するための関数
    
    output_dir = "output/iterated_prisoner"
    os.makedirs(output_dir, exist_ok=True)

    odd_rows = df[df.index % 2 == 0]
    even_rows = df[df.index % 2 == 1]

    odd_rows.columns = [f'{col}_p1' for col in odd_rows.columns]

    even_rows.columns = [f'{col}_p2' for col in even_rows.columns]

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
    ]

    result = result[new_column_order]

    result_sorted = result.sort_values(by='session_p1')

    
    result_sorted.to_csv(f'output/iterated_prisoner/iterated_prisoner_{filename_number}.csv', encoding='utf-8-sig', index=False)


if __name__ == "__main__":
    # テスト用のデータフレームを作成
    df = pd.DataFrame(columns=['session', 'player', 'round', 'cooperate', 'payoff', 'start_time', 'choice_time'])

    write_to_csv(df, 1)