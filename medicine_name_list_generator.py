import PySimpleGUI as sg
from data_set_formatter import DataSetFormatter 

# 画面のテーマカラーを水色に指定
sg.theme("LightBlue")

# 描画する画面をここで作成
layout = [
    [sg.Text("Excelファイルを選択してください")],
    [sg.Text("内用薬"),sg.InputText(),sg.FileBrowse(key="file_oral")],
    [sg.Text("注射薬"),sg.InputText(),sg.FileBrowse(key="file_injection")],
    [sg.Text("外用薬"),sg.InputText(),sg.FileBrowse(key="file_topical")],
    [sg.Submit("実行")]
]

# Windowを生成し、タイトルと描画する画面をわたす
window = sg.Window("Medicine Name List Generator", layout)

while True:
    # イベントと値を管理する変数を取得
    event, values = window.read()
    
    # xボタンが押されるとWIN_CLOSEDがtureになり、ループが終了
    if event == sg.WIN_CLOSED:
        break
    # 実行ボタンが押された時の処理    
    elif event == "実行":
        # 内用薬、注射薬、外用薬のデータのファイルパスを取得
        file_path_oral = values["file_oral"]
        file_path_injection = values["file_injection"]
        file_path_topical = values["file_topical"]
        # パスが取得できたら
        if file_path_oral != "" and file_path_injection != "" and file_path_topical != "":
            # CSVファイルを作成
            data_set_formatter = DataSetFormatter()
            data_set_formatter.create_csv(file_path_oral, file_path_injection, file_path_topical)
# ループが終了すると、画面が閉じる 
window.close()
