import pandas as pd
import re

# データセット加工用のクラス
class DataSetFormatter:
    # を作成するメソッド
    def create_csv(self, file_path_oral, file_path_injection, file_path_topical):
        # 内用薬のデータを取得
        df_oral = pd.read_excel(file_path_oral)
        # 注射薬のデータを取得
        df_injection = pd.read_excel(file_path_injection)
        # 外用薬のデータを取得
        df_topical = pd.read_excel(file_path_topical)

        # 内用薬、注射薬、外用薬に対して、個別のデータセット加工処理を行う
        df_oral_processed = self.process_oral(df_oral)
        df_injection_processed = self.process_injection(df_injection)
        df_topical_processed = self.process_topical(df_topical)
        
        # データを結合
        df_final = pd.concat([df_oral_processed, df_injection_processed, df_topical_processed], ignore_index=True)
        
        # CSVに出力
        df_final.to_csv('medicine_name_list.csv', index = False)
        

    # 内用薬についてのデータ加工処理
    def process_oral(self, df):
        # コピーを作成してから変更を行う
        df_oral = df.copy()
        # 先発品名でフィルター
        df = self.filter_by_original_name(df_oral)
        # 区分, 成分名, 品名で、射影
        df = self.select_categories_and_generic_name_and_brand_name(df)
        #  品名からカタカナ部分を抽出
        df['商品名'] = df['品名'].apply(self.extract_first_katakana)
        #不要なカタカナをさらに排除
        df['商品名'] = df['商品名'].str.replace('カプセルセット', '').str.replace('カプセル', '').str.replace('ドライシロップ', '').str.replace('シロップ', '').str.replace('コーワ', '').str.replace('チュアブル', '').str.replace('レディタブ', '').str.replace('ザイディス', '').str.replace("エリキシル", "").str.replace('バッカル', '').str.replace('ゲル', '').str.replace('・リキッド', '').str.replace('ヘパン', 'ヘパンED').str.replace('バクタミニ', '')
        # 成分名から特定の文字を削除・または、変更
        df['成分名'] = df['成分名'].str.replace('（遺伝子組換え）', '')
        # 品名に会社名を含む行をドロップ
        df = self.drop_medicine_with_company_name(df)
        # 商品名の最後の3文字が 'パック' の場合、その部分を削除
        df['商品名'] = df['商品名'].apply(self.remove_pack)
        # ドット（・）をドロップ
        df['商品名'] = df['商品名'].apply(self.remove_trailing_dot)
        # 例外 'モルヒネ硫酸塩水和物' '→ MSコンチン'
        name_list = [('モルヒネ硫酸塩水和物', 'MSコンチン'),
                     ('Ｌ－アルギニン・Ｌ－アルギニン塩酸塩', 'アルギU'),
                     ('イルソグラジンマレイン酸塩', 'ガスロンN'),
                     ('コレスチミド', 'コレバイン'),
                     ('スギ花粉エキス', 'シダキュア'),
                     ('ダニアレルゲンエキス', 'ミティキュア'),
                     ('プロカテロール塩酸塩水和物', 'メプチン'),
                     ('ドロスピレノン・エチニルエストラジオール　ベータデクス', 'ヤーズ'),
                     ('リン酸ジソピラミド', '')]
        for names in name_list:
            df = self.update_brand_name_by_component(df, names[0], names[1])  
        # 全角の英語を半角の英語に変換
        df['商品名'] = df['商品名'].apply(self.half_width)
        df['成分名'] = df['成分名'].apply(self.half_width)
        # 全角スペースを半角にする
        df['成分名'] = df['成分名'].str.replace('　', ' ')
        # データセットの品名の列の文字列が、同じ行の成分名の文字を含んでいたらその行を削除する
        df = self.drop_name_where_product_name_has_ingredient_name(df)
        # 商品名が空白の行をドロップ
        df = self.drop_na(df)
        # 区分番号を割り当て
        df['区分番号'] = df['区分'].apply(self.assign_category_number)
        # '区分番号', '区分', '商品名', '一般名'の表にする
        df = df[['区分番号', '区分', '商品名', '成分名']].rename(columns={'成分名': '一般名'})
        # 重複を削除
        df = df.drop_duplicates()
        #データセットをソート
        df = df.sort_values(by=['区分番号', '商品名']).reset_index(drop=True)
        return df

    # 注射薬についてのデータ加工処理
    def process_injection(self, df):
        # コピーを作成してから変更を行う
        df_injection = df.copy()
        # 先発品名でフィルター
        df = self.filter_by_original_name(df_injection)
        # 区分, 成分名, 品名で、射影
        df = self.select_categories_and_generic_name_and_brand_name(df)
        #  品名からカタカナ部分を抽出
        df['商品名'] = df['品名'].apply(self.extract_first_katakana)
        # ドット（・）をドロップ
        df['商品名'] = df['商品名'].apply(self.remove_trailing_dot)
        # リンをリン酸Na補正液に戻す
        df['商品名'] = df['商品名'].apply(self.modify_phosphate_na_solution)
        #不要なカタカナをさらに排除
        df['商品名'] = df['商品名'].str.replace('・プリモビスト', 'EOB・プリモビスト').str.replace('ディスポ', '').str.replace('ミックス', '').str.replace('キット', '').str.replace('グランシリンジ', '').str.replace('ゴークイック', '').str.replace('ドライ', 'Dドライ')
        # 成分名から特定の文字を削除・または、変更
        df['成分名'] = df['成分名'].str.replace('（遺伝子組換え）', '')
        # 品名に会社名を含む行をドロップ
        df = self.drop_medicine_with_company_name(df)
        name_list = [
        ('エポプロステノールナトリウム専用溶解液', '静注用フローラン専用溶解液'),
        ('テトラコサクチド酢酸塩', 'コートロシン注射用'),
        ('酢酸テトラコサクチド亜鉛', 'コートロシンＺ筋注'),
        ('ブドウ糖加酢酸リンゲル', 'ヴィーンＤ輸液'),
        ('酢酸リンゲル', 'ヴィーンＦ輸液'),
        ('酢酸維持液（ブドウ糖加）', 'ヴィーン３Ｇ輸液'),
        ('ベンダムスチン塩酸塩水和物', 'トレアキシン点滴静注液'),
        ('ベンダムスチン塩酸塩', 'トレアキシン点滴静注用'),
        ('ミリプラチン水和物', 'ミリプラ動注用'),
        ('ジエチレントリアミン五酢酸テクネチウム（９９ｍＴｃ）', 'テクネＤＴＰＡキット'),
        ('メチレンジホスホン酸テクネチウム（９９ｍＴｃ）', 'テクネＭＤＰ注射液'),
        ('テクネチウム大凝集人血清アルブミン（９９ｍＴｃ）', 'テクネＭＡＡキット'),
        ('テトラキスメトキシイソブチルイソニトリル銅（Ｉ）四フッ化ホウ酸', 'カーディオライト'),
        ('ヘキサキスメトキシイソブチルイソニトリルテクネチウム（９９ｍＴｃ）', 'カーディオライト注射液'),
        ('ベンゾイルメルカプトアセチルグリシルグリシルグリシン', 'テクネＭＡＧ３キット'),
        ('メルカプトアセチルグリシルグリシルグリシンテクネチウム（９９ｍＴｃ）', 'テクネＭＡＧ３注射液'),
        ('ヨード化ケシ油脂肪酸エチルエステル', 'ミリプラ用懸濁用液'),
        ('ヒドロキソコバラミン', 'シアノキット'),
        ('３－ヨードベンジルグアニジン（１２３Ｉ）', 'ミオMIBG'),
        ('３－ヨードベンジルグアニジン（１３１Ｉ）', 'ライアットMIBG')
        ]
        for names in name_list:
            df = self.update_brand_name_by_component(df, names[0], names[1])
        # 全角の英語を半角の英語に変換
        df['商品名'] = df['商品名'].apply(self.half_width)
        df['成分名'] = df['成分名'].apply(self.half_width)
        # 全角スペースを半角にする
        df['成分名'] = df['成分名'].str.replace('　', ' ')
        # データセットの品名の列の文字列が、同じ行の成分名の文字を含んでいたらその行を削除する
        df = self.drop_name_where_product_name_has_ingredient_name(df)
        # 商品名が空白の行をドロップ
        df = self.drop_na(df)
        # 区分番号を割り当て
        df['区分番号'] = df['区分'].apply(self.assign_category_number)
        # '区分番号', '区分', '商品名', '一般名'の表にする
        df = df[['区分番号', '区分', '商品名', '成分名']].rename(columns={'成分名': '一般名'})
        # 重複を削除
        df = df.drop_duplicates()
        #データセットをソート
        df = df.sort_values(by=['区分番号', '商品名']).reset_index(drop=True)
        return df

    # 外用薬についてのデータ加工処理
    def process_topical(self, df):
        # コピーを作成してから変更を行う
        df_topical = df.copy()
        # 先発品名でフィルター
        df = self.filter_by_original_name(df_topical)
        # 区分, 成分名, 品名で、射影
        df = self.select_categories_and_generic_name_and_brand_name(df)
        #  品名からカタカナ部分を抽出
        df['商品名'] = df['品名'].apply(self.extract_first_katakana)
        # 小数点を'0'に変換
        df['商品名'] = df['品名'].apply(self.replace_dot_with_zero)
        # 数字部分を削除
        df['商品名'] = df['商品名'].apply(self.remove_digit)
        #不要な文字をさらに排除
        df['商品名'] = df['商品名'].str.replace('ｍｇ', '').str.replace('ｍＬ', '').str.replace('％', '').str.replace('μｇ', '').str.replace('ｇ', '').str.replace('／', '').str.replace('ｃ㎡', '').str.replace('回', '').str.replace('中用量', '').str.replace('低用量', '').str.replace('高用量', '').str.replace('小児用', '').str.replace('ミニ点眼液', '点眼液')
        # 成分名から特定の文字を削除・または、変更
        df['成分名'] = df['成分名'].str.replace('（遺伝子組換え）', '')
        # 品名に会社名を含む行をドロップ
        df = self.drop_medicine_with_company_name(df)
        # 商品名の最後の3文字が '吸入用' の場合、その部分を削除
        df['商品名'] = df['商品名'].apply(self.remove_kyunyuyo)
        # 商品名の最後の3文字が '噴霧用' の場合、その部分を削除
        df['商品名'] = df['商品名'].apply(self.remove_funmuyo)
        # 商品名の最後の2文字が '吸入' の場合、その部分を削除
        df['商品名'] = df['商品名'].apply(self.remove_kyunyu)
        # 例外
        name_list = [('フルオロウラシル', '5-FU軟膏')]
        for names in name_list:
            df = self.update_brand_name_by_component(df, names[0], names[1])
        # 全角の英語を半角の英語に変換
        df['商品名'] = df['商品名'].apply(self.half_width)
        df['成分名'] = df['成分名'].apply(self.half_width)
        # 全角スペースを半角にする
        df['成分名'] = df['成分名'].str.replace('　', ' ')
        # データセットの品名の列の文字列が、同じ行の成分名の文字を含んでいたらその行を削除する
        df = self.drop_name_where_product_name_has_ingredient_name(df)
        # 商品名が空白の行をドロップ
        df = self.drop_na(df)
        # 区分番号を割り当て
        df['区分番号'] = df['区分'].apply(self.assign_category_number)
        # '区分番号', '区分', '商品名', '一般名'の表にする
        df = df[['区分番号', '区分', '商品名', '成分名']].rename(columns={'成分名': '一般名'})
        # 重複を削除
        df = df.drop_duplicates()
        #データセットをソート
        df = df.sort_values(by=['区分番号', '商品名']).reset_index(drop=True)
        return df

    
    # 先発品に絞り込む
    def filter_by_original_name(self, df):
        return df[df['先発医薬品'] == '先発品']
    
    # 区分, 成分名, 品名で、射影
    def select_categories_and_generic_name_and_brand_name(self, df):
        selected_columns = df[['区分', '成分名', '品名']]
        return selected_columns

    # カタカナ部分を抽出
    def extract_first_katakana(self, input_text):
        match = re.search(r'[\u30A0-\u30FFー]+', input_text)
        return match.group() if match else ''
    
    # 品名に会社名を含む行を削除
    def drop_medicine_with_company_name(self, df):
        # 特定の列に「」を含む行をドロップ
        df = df[~df['品名'].str.contains('「.*」')]
        # 特定の列に（）を含む行をドロップ
        df = df[~df['品名'].str.contains('（.*）')]
        return df

    # 商品名の最後の3文字が 'パック' の場合、その部分を削除する関数
    def remove_pack(self, name):
        if name.endswith('パック'):
            return name[:-3]  # 最後の3文字を削除した文字列を返す
        else:
            return name

    # 商品名の最後の3文字が '吸入用' の場合、その部分を削除する関数
    def remove_kyunyuyo(self, name):
        if name.endswith('吸入用'):
            return name[:-3]  # 最後の3文字を削除した文字列を返す
        else:
            return name
            
    # 商品名の最後の2文字が '吸入' の場合、その部分を削除する関数
    def remove_kyunyu(self, name):
        if name.endswith('吸入'):
            return name[:-2]  # 最後の2文字を削除した文字列を返す
        else:
            return name
            
    # 商品名の最後の3文字が '噴霧用' の場合、その部分を削除する関数
    def remove_funmuyo(self, name):
        if name.endswith('噴霧用'):
            return name[:-3]  # 最後の3文字を削除した文字列を返す
        else:
            return name

    # ドット（・）をドロップ
    def remove_trailing_dot(self, input_text):
        return input_text.rstrip('・')

    # 例外の文字列を置換
    def update_brand_name_by_component(self, df, component_name, new_brand_name):
        """
        成分名が指定された値の場合、先発品名を指定された値に更新する関数
        Parameters:
        - df: 対象のDataFrame
        - component_name: 更新条件となる成分名の値
        - new_brand_name: 更新後の先発品名の値
        Returns:
        - 更新後のDataFrame
        """
        # 成分名が指定された値の行を取得
        condition_rows = df[df['成分名'] == component_name]
        # 先発品名を指定された値に更新
        df.loc[condition_rows.index, '商品名'] = new_brand_name
        return df

    # 全角文字を半角に変換
    def half_width(self, text):
        # 全角のアルファベットを半角に変換
        text = text.translate(str.maketrans('ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        # 全角の数字を半角に変換
        text = text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        # ハイフンの変換
        text = text.replace("－", "-")
        return text

    # 品名に成分名を含む行をドロップする
    def drop_name_where_product_name_has_ingredient_name(self, df):
        return df[~df.apply(lambda row: row['成分名'] in row['商品名'], axis=1)]

    # NaNをドロップ
    def drop_na(self, df):
    # コピーを作成してから変更を行う
        df_copy = df.copy()
    # 空白の値を持つ行をNaNに変換してからドロップ
        df_copy.replace('', float('nan'), inplace=True)
        df_dropped_na = df_copy.dropna()
        return df_dropped_na
        
    # 区分に基づいて区分番号を生成する関数
    def assign_category_number(self, category):
        if category == '内用薬':
            return 0
        elif category == '注射薬':
            return 1
        elif category == '外用薬':
            return 2
        else:
            return -1  # 未知の区分の場合、-1を返す

    # 'リン' → 'リン酸Ｎａ補正液'
    def modify_phosphate_na_solution(self, input_text):
        return 'リン酸Ｎａ補正液' if 'リン' == input_text else input_text

    # 正規表現を使用して「．」を0に置き換え
    def replace_dot_with_zero(self, input_text):
        return re.sub(r'．', '0', input_text)

    # 正規表現を使用して数字部分を削除
    def remove_digit(self, text):
        return re.sub(r'\d+', '', text)
