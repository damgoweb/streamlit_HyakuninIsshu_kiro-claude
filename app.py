import streamlit as st
import json
import random
from dataclasses import dataclass
from typing import List, Dict, Optional

# データクラス定義
@dataclass
class Poem:
    id: int
    author: str
    upper: str  # 上の句
    lower: str  # 下の句
    reading_upper: str  # 上の句読み
    reading_lower: str  # 下の句読み
    description: str  # 解説

@dataclass
class Question:
    poem: Poem
    question_text: str  # 問題文（上の句 or 全句）
    choices: List[str]  # 選択肢
    correct_answer: str  # 正解
    question_type: str  # "lower_verse" or "author"

@dataclass
class Score:
    correct: int
    total: int
    
    @property
    def percentage(self) -> float:
        return (self.correct / self.total * 100) if self.total > 0 else 0

# データ管理コンポーネント
class HyakuninIsshuData:
    def __init__(self, json_path: str = "./hyakunin_isshu.json"):
        self.json_path = json_path
        self.poems: List[Poem] = []
        self.load_data()
    
    def load_data(self) -> List[Dict]:
        """JSONファイルからデータを読み込む"""
        try:
            # 実際のJSONファイルから読み込み
            with open(self.json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # データ検証
            if not isinstance(data, list):
                raise ValueError("JSONデータはリスト形式である必要があります")
            
            # データをPoemオブジェクトに変換
            self.poems = []
            for poem_data in data:
                # 必須フィールドの確認
                required_fields = ['id', 'author', 'upper', 'lower', 
                                 'reading_upper', 'reading_lower', 'description']
                for field in required_fields:
                    if field not in poem_data:
                        raise ValueError(f"必須フィールド '{field}' が見つかりません")
                
                poem = Poem(**poem_data)
                self.poems.append(poem)
            
            if len(self.poems) == 0:
                raise ValueError("有効なデータが見つかりません")
                
            return data
            
        except FileNotFoundError:
            st.error(f"ファイルが見つかりません: {self.json_path}")
            self._load_fallback_data()
            return []
        except json.JSONDecodeError as e:
            st.error(f"JSONファイルの形式が正しくありません: {e}")
            self._load_fallback_data()
            return []
        except Exception as e:
            st.error(f"データ読み込みエラー: {e}")
            self._load_fallback_data()
            return []
    
    def _load_fallback_data(self):
        """フォールバック用のサンプルデータを読み込み"""
        fallback_data = [
            {
                "id": 1,
                "author": "天智天皇",
                "upper": "秋の田の かりほの庵の 苫をあらみ",
                "lower": "わが衣手は 露にぬれつつ",
                "reading_upper": "あきのたの かりほのいほの とまをあらみ",
                "reading_lower": "わがころもでは つゆにぬれつつ",
                "description": "稲刈り期の仮小屋での体験を詠んだ歌"
            },
            {
                "id": 2,
                "author": "持統天皇",
                "upper": "春過ぎて 夏来にけらし 白妙の",
                "lower": "衣ほすてふ 天の香具山",
                "reading_upper": "はるすぎて なつきにけらし しろたえの",
                "reading_lower": "ころもほすてふ あまのかぐやま",
                "description": "季節の移ろいを香具山の情景で詠んだ歌"
            },
            {
                "id": 3,
                "author": "柿本人麻呂",
                "upper": "あしびきの 山鳥の尾の しだり尾の",
                "lower": "ながながし夜を ひとりかも寝む",
                "reading_upper": "あしびきの やまどりのおの しだりおの",
                "reading_lower": "ながながしよを ひとりかもねむ",
                "description": "長い夜の孤独を山鳥の尾に例えた恋歌"
            },
            {
                "id": 4,
                "author": "山部赤人",
                "upper": "田子の浦に うち出でて見れば 白妙の",
                "lower": "富士の高嶺に 雪は降りつつ",
                "reading_upper": "たごのうらに うちいでてみれば しろたえの",
                "reading_lower": "ふじのたかねに ゆきはふりつつ",
                "description": "田子の浦から望む富士の嶺に、雪がしきりに降る清澄の景"
            },
            {
                "id": 5,
                "author": "猿丸太夫",
                "upper": "奥山に もみぢ踏み分け 鳴く鹿の",
                "lower": "声聞く時ぞ 秋は悲しき",
                "reading_upper": "おくやまに もみぢふみわけ なくしかの",
                "reading_lower": "こえきくときぞ あきはかなしき",
                "description": "奥山で鹿の声を聞く瞬間、秋の寂寥が胸に満ちる"
            }
        ]
        
        self.poems = []
        for poem_data in fallback_data:
            poem = Poem(**poem_data)
            self.poems.append(poem)
        
        st.warning("サンプルデータを使用しています。正しいJSONファイルを配置してください。")
    
    def get_random_poem(self) -> Optional[Poem]:
        """ランダムに1首を取得"""
        if self.poems:
            return random.choice(self.poems)
        return None
    
    def get_random_poems(self, count: int) -> List[Poem]:
        """ランダムに複数首を取得"""
        if len(self.poems) >= count:
            return random.sample(self.poems, count)
        return self.poems.copy()

# ゲーム管理コンポーネント
class GameManager:
    def __init__(self, data: HyakuninIsshuData):
        self.data = data
    
    def generate_lower_verse_question(self) -> Optional[Question]:
        """下の句当て問題を生成"""
        if len(self.data.poems) < 4:
            st.error("問題生成に必要な歌が不足しています（最低4首必要）")
            return None
        
        try:
            # 正解となる歌を選択
            correct_poem = self.data.get_random_poem()
            if not correct_poem:
                return None
            
            # 選択肢用の歌を3首選択（正解を除く）
            other_poems = [p for p in self.data.poems if p.id != correct_poem.id]
            choice_poems = random.sample(other_poems, 3)
            
            # 選択肢を作成（下の句）
            choices = [poem.lower for poem in choice_poems]
            choices.append(correct_poem.lower)
            random.shuffle(choices)
            
            # 問題オブジェクトを作成
            question = Question(
                poem=correct_poem,
                question_text=correct_poem.upper,
                choices=choices,
                correct_answer=correct_poem.lower,
                question_type="lower_verse"
            )
            
            return question
            
        except Exception as e:
            st.error(f"問題生成エラー: {e}")
            return None
    
    def generate_author_question(self) -> Optional[Question]:
        """作者当て問題を生成"""
        if len(self.data.poems) < 4:
            st.error("問題生成に必要な歌が不足しています（最低4首必要）")
            return None
        
        try:
            # 正解となる歌を選択
            correct_poem = self.data.get_random_poem()
            if not correct_poem:
                return None
            
            # 選択肢用の歌を3首選択（正解を除く）
            other_poems = [p for p in self.data.poems if p.id != correct_poem.id]
            choice_poems = random.sample(other_poems, 3)
            
            # 選択肢を作成（作者名）
            choices = [poem.author for poem in choice_poems]
            choices.append(correct_poem.author)
            # 重複削除して再度選択肢を調整
            choices = list(set(choices))
            
            # 選択肢が4つ未満の場合、追加で歌を選択
            while len(choices) < 4 and len(other_poems) > len(choices) - 1:
                additional_poems = [p for p in other_poems 
                                 if p.author not in choices and p.id != correct_poem.id]
                if additional_poems:
                    additional_poem = random.choice(additional_poems)
                    choices.append(additional_poem.author)
                else:
                    break
            
            random.shuffle(choices)
            
            # 問題文（上の句＋下の句）
            question_text = f"{correct_poem.upper}\n{correct_poem.lower}"
            
            # 問題オブジェクトを作成
            question = Question(
                poem=correct_poem,
                question_text=question_text,
                choices=choices,
                correct_answer=correct_poem.author,
                question_type="author"
            )
            
            return question
            
        except Exception as e:
            st.error(f"問題生成エラー: {e}")
            return None
    
    def check_answer(self, user_answer: str, correct_answer: str) -> bool:
        """回答判定"""
        return user_answer == correct_answer
    
    def update_score(self, is_correct: bool):
        """スコア更新"""
        if 'score' not in st.session_state:
            st.session_state.score = Score(0, 0)
        
        if is_correct:
            st.session_state.score.correct += 1
        st.session_state.score.total += 1
    
    def reset_game(self):
        """ゲームリセット"""
        st.session_state.score = Score(0, 0)
        if 'current_question' in st.session_state:
            del st.session_state.current_question
        if 'show_result' in st.session_state:
            del st.session_state.show_result
        if 'user_answer' in st.session_state:
            del st.session_state.user_answer
        if 'question_answered' in st.session_state:
            del st.session_state.question_answered

# セッション状態初期化
def initialize_session_state():
    """Streamlit Session Stateの初期化"""
    if 'data' not in st.session_state:
        st.session_state.data = HyakuninIsshuData()
    
    if 'game_manager' not in st.session_state:
        st.session_state.game_manager = GameManager(st.session_state.data)
    
    if 'game_mode' not in st.session_state:
        st.session_state.game_mode = "下の句当て"  # デフォルトモード
    
    if 'score' not in st.session_state:
        st.session_state.score = Score(0, 0)
    
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = None
    
    if 'question_answered' not in st.session_state:
        st.session_state.question_answered = False

def reset_question_state():
    """問題関連の状態をリセット"""
    st.session_state.current_question = None
    st.session_state.user_answer = None
    st.session_state.show_result = False
    st.session_state.question_answered = False

def generate_new_question():
    """新しい問題を生成"""
    reset_question_state()
    
    if st.session_state.game_mode == "下の句当て":
        question = st.session_state.game_manager.generate_lower_verse_question()
    else:  # 作者当て
        question = st.session_state.game_manager.generate_author_question()
    
    st.session_state.current_question = question
    return question

def handle_answer_click(selected_choice: str):
    """回答選択時の処理"""
    if not st.session_state.question_answered:
        st.session_state.user_answer = selected_choice
        st.session_state.question_answered = True
        
        # 正誤判定
        question = st.session_state.current_question
        is_correct = st.session_state.game_manager.check_answer(
            selected_choice, question.correct_answer
        )
        
        # スコア更新
        st.session_state.game_manager.update_score(is_correct)
        st.session_state.show_result = True
        
        # 画面を更新
        st.rerun()

def render_game_ui():
    """ゲームUI表示"""
    # 現在の問題がない場合は新しい問題を生成
    if st.session_state.current_question is None:
        generate_new_question()
    
    question = st.session_state.current_question
    if not question:
        st.error("問題を生成できませんでした。")
        return
    
    # 問題表示
    st.markdown('<div class="question-area">', unsafe_allow_html=True)
    if question.question_type == "lower_verse":
        st.markdown("### 📝 上の句から下の句を選んでください")
        st.markdown(f'<div class="poem-text">{question.question_text}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="poem-reading">({question.poem.reading_upper})</div>', unsafe_allow_html=True)
    else:  # author
        st.markdown("### 📝 この歌の作者を選んでください")
        st.markdown(f'<div class="poem-text">{question.question_text}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="poem-reading">({question.poem.reading_upper})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="poem-reading">({question.poem.reading_lower})</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 選択肢表示
    st.markdown("### 選択肢")
    
    # 回答済みかどうかで処理を分岐
    if not st.session_state.question_answered:
        # 未回答の場合：選択肢ボタンを表示
        cols = st.columns(1)
        for i, choice in enumerate(question.choices, 1):
            if st.button(f"{i}. {choice}", key=f"choice_{i}", use_container_width=True):
                handle_answer_click(choice)
    else:
        # 回答済みの場合：結果表示
        user_answer = st.session_state.user_answer
        correct_answer = question.correct_answer
        is_correct = user_answer == correct_answer
        
        # 選択肢を色分けして表示
        for i, choice in enumerate(question.choices, 1):
            if choice == correct_answer:
                # 正解の選択肢
                st.markdown(f'<div class="result-correct">✅ {i}. {choice} (正解)</div>', 
                           unsafe_allow_html=True)
            elif choice == user_answer and not is_correct:
                # 不正解の選択肢（ユーザーが選択）
                st.markdown(f'<div class="result-incorrect">❌ {i}. {choice} (あなたの回答)</div>', 
                           unsafe_allow_html=True)
            else:
                # その他の選択肢
                st.markdown(f'<div style="padding: 0.5rem; margin: 0.25rem 0; border: 1px solid #ddd; border-radius: 5px;">{i}. {choice}</div>', 
                           unsafe_allow_html=True)
        
        # 結果メッセージ
        if is_correct:
            st.success("🎉 正解です！")
        else:
            st.error("❌ 不正解です。")
        
        # 解説表示
        st.markdown('<div class="description-area">', unsafe_allow_html=True)
        st.markdown("#### 📚 解説")
        st.markdown(f"**作者**: {question.poem.author}")
        st.markdown(f"**全文**:")
        st.markdown(f"{question.poem.upper}")
        st.markdown(f"{question.poem.lower}")
        st.markdown(f"**読み**:")
        st.markdown(f"{question.poem.reading_upper}")
        st.markdown(f"{question.poem.reading_lower}")
        st.markdown(f"**解説**: {question.poem.description}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 次の問題ボタン
        if st.button("🔄 次の問題", use_container_width=True):
            generate_new_question()
            st.rerun()

# UIコンポーネント
def apply_custom_css():
    """カスタムCSSスタイルを適用"""
    st.markdown("""
    <style>
    /* メインテーマ */
    .main-header {
        text-align: center;
        color: #1e3a8a;
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        margin-bottom: 1rem;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* 問題表示エリア */
    .question-area {
        background: linear-gradient(135deg, #fef7ed 0%, #fff7ed 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #fbbf24;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 和歌テキスト */
    .poem-text {
        font-size: 1.5rem;
        line-height: 1.8;
        color: #1e3a8a;
        text-align: center;
        margin: 1rem 0;
        font-weight: 600;
    }
    @media (max-width: 600px) {
        .main-header {
            font-size: clamp(1.2rem, 8vw, 2rem) !important;
        }
        .poem-text {
            font-size: 1.2rem;
        }
        .stButton > button {
            font-size: 1.1rem;
        }
    }    
    @media (prefers-color-scheme: dark) {
        .poem-text {
            color: #fff !important;
            text-shadow: 0 1px 4px #222;
        }
        .question-area {
            background: linear-gradient(135deg, #222 0%, #333 100%);
            border: 2px solid #fbbf24;
        }
    }                
    .poem-reading {
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        font-style: italic;
        margin-bottom: 1rem;
    }
    
    /* 選択肢ボタン */
    .stButton > button {
        width: 100%;
        min-height: 60px;
        font-size: 1.3rem;
        border-radius: 10px;
        border: 2px solid #1e3a8a;
        background-color: #ffffff;
        color: #1e3a8a;
        font-weight: 500;
        padding: 10px;
        text-align: left;
        white-space: normal;
    }
    
    .stButton > button:hover {
        background-color: #1e3a8a;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(30, 58, 138, 0.3);
    }
    
    /* 正解・不正解の表示 */
    .result-correct {
        background-color: #dcfce7;
        border: 2px solid #10b981;
        color: #059669;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.25rem 0;
        font-weight: bold;
    }
    
    .result-incorrect {
        background-color: #fef2f2;
        border: 2px solid #ef4444;
        color: #dc2626;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.25rem 0;
        font-weight: bold;
    }
    
    /* 解説エリア */
    .description-area {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #fbbf24;
        margin: 1rem 0;
    }
    
    /* サイドバー */
    .css-1d391kg {
        background-color: #fef7ed;
    }
    
    /* スコア表示 */
    .score-display {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """アプリケーションヘッダー"""
    apply_custom_css()
    st.markdown('<h1 class="main-header">🌸 百人一首クイズ 🌸</h1>', unsafe_allow_html=True)
    st.markdown("### 📚 古典文学を楽しく学ぼう")
    st.write("Pwored by Kiro + Claude")

    st.markdown("---")

def render_sidebar():
    """サイドバー"""
    st.sidebar.title("ゲーム設定")
    
    # ゲームモード選択
    game_modes = ["下の句当て", "作者当て"]
    selected_mode = st.sidebar.selectbox(
        "ゲームモード",
        game_modes,
        index=game_modes.index(st.session_state.game_mode)
    )
    
    if selected_mode != st.session_state.game_mode:
        st.session_state.game_mode = selected_mode
        reset_question_state()  # モード変更時に問題をリセット
        st.rerun()
    
    # スコア表示
    st.sidebar.markdown("### 📊 スコア")
    score = st.session_state.score
    st.sidebar.metric("正解数", f"{score.correct}/{score.total}")
    if score.total > 0:
        st.sidebar.metric("正解率", f"{score.percentage:.1f}%")
    
    # リセットボタン
    if st.sidebar.button("🔄 スコアリセット"):
        st.session_state.game_manager.reset_game()
        st.rerun()
    
    # 新しい問題ボタン
    if st.sidebar.button("🎲 新しい問題"):
        generate_new_question()
        st.rerun()

# メイン関数
def main():
    # ページ設定
    st.set_page_config(
        page_title="百人一首クイズ Kiro+Claude",
        page_icon="🌸",
        layout="wide"
    )
    
    # セッション状態初期化
    initialize_session_state()
    
    # ヘッダー表示
    render_header()
    
    # サイドバー表示
    render_sidebar()
    
    # メインゲームエリア
    st.header(f"🎯 {st.session_state.game_mode}")
    
    # ゲームUI表示
    render_game_ui()

if __name__ == "__main__":
    main()