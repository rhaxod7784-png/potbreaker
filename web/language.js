(()=> {
const dictionaries = {
en: {
"폿브레이커 RE | 기묘와 크다 부장의 사무실 미로":"POT BREAKER RE | Gimyo vs. Manager Keuda",
"POT BREAKER RE v1.0.97":"POT BREAKER RE v1.0.97",
"기묘가 CBZP에 출근하고, 이상한 사무실에서 화분을 피하고 크다 부장에게 쫓기는 4컷 만화":"A four-panel comic: Gimyo starts at CBZP, dodges flying pots, and is chased by Manager Keuda.",
"기묘와 크다 부장의 사무실 미로 추격전":"Office Maze Chase: Gimyo vs. Manager Keuda",
"CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.":"Play as Gimyo, a CBZP cat intern. Dodge Manager Keuda and throw pots in this browser maze game.",
"기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.":"A free browser maze game: guide Gimyo through the CBZP office. Read the game guide, controls, privacy and advertising information.",
"고양이 인턴 기묘와 악어 부장 크다의 CBZP 사무실 미로 추격전.":"A CBZP office maze chase starring cat intern Gimyo and crocodile manager Keuda.",
"게임 시작":"Start Game","🏆 랭킹":"🏆 Rankings","게임 방법":"How to Play",
"방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.":"Move with the directional pad, dash to dodge, and throw pots. The match ends when either character runs out of HP.",
"게임 소개와 조작법":"Game Guide & Controls","개인정보 및 광고 안내":"Privacy & Ads",
"이상한 회사의":"A Strange","인턴 생활":"Company Internship","정말... 이 회사에서":"Can I really survive","살아남을 수 있을까?":"at this company?",
"난이도":"Difficulty","노멀":"Normal","하드":"Hard","베리 하드":"Very Hard","베리 하드":"Very Hard","베리 하드":"Very Hard",
"사무실로 입장 ▶":"Enter the Office ▶","기묘 / PLAYER":"Gimyo / PLAYER","크다 부장 / NPC":"Manager Keuda / NPC",
"대시":"Dash","던지기":"Throw","↻ 다시 도전":"↻ Play Again","처음으로":"Home","랭킹 등록":"Submit Score",
"🏆 POT BREAKER 랭킹":"🏆 POT BREAKER Rankings","닉네임":"Nickname","최대 16자":"Up to 16 characters",
"랭킹을 불러오는 중…":"Loading rankings…","사무실 문을 열고 있습니다":"Opening the office door","Python 게임 엔진을 준비하고 있습니다.":"Preparing the Python game engine.",
"다시 시도하기":"Try Again","잠깐 휴식!":"Take a Break!","계속하기":"Resume","아직 등록된 클리어 기록이 없습니다.":"No completed runs have been recorded yet.",
"랭킹을 불러오지 못했습니다.":"Could not load rankings.","서버 연결에 실패했습니다.":"Could not connect to the server.",
"랭킹에 등록했습니다.":"Score submitted.","Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.":"Could not load Pyodide. Check your internet connection.",
"게임 엔진을 불러오지 못했습니다.":"Could not load the game engine.","게임을 불러오지 못했습니다.":"Could not load the game.",
"게임 화면 갱신 오류:":"Game screen update error:","기묘 승리!":"Gimyo Wins!","크다 부장 승리!":"Manager Keuda Wins!",
"화분 한 방! 크다 부장의 뚝배기를 깼습니다.":"One pot hit! Manager Keuda is down.","기묘가 화분에 머리만 내놓고 심어졌습니다…":"Gimyo got planted with only their head above the pot…",
"쨍그랑!":"Crash!","감 과장":"Manager Gam","랭킹 닫기":"Close rankings",
"♥ 회복 · 감 과장: ? 화분 4종 (하트 ±1 · 화분 풀충전 · 필드 리셋, 각 25%) · 기묘: 대시 3초 / 크다: 대시 5초 · 원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"♥ Heal · Manager Gam: 4 random pot effects (±1 heart, refill pots, reset field; 25% each) · Gimyo dash: 3s / Keuda dash: 5s · Use the circular pad to move; hold to keep moving",
"원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"Use the circular pad to move · Hold to keep moving",
"화분: 공격 · 대시 버튼: 3칸 돌진 (3초 재사용)":"Pots: attack · Dash: 3 tiles (3s cooldown)",
"PC: 방향키 / WASD · Space(공격) · Shift(대시)":"PC: Arrows / WASD · Space (throw) · Shift (dash)",
"언어 변경":"Change language","언어 선택":"Select language","게임 안내":"Game Guide",
"대시 버튼: 3칸 돌진 · 3초 재사용 대기":"Dash: move 3 tiles · 3-second cooldown",
"감 과장 출동!":"Manager Gam is here!",
"화분 투하!":"Pots incoming!",
"크다":"Keuda",
"기묘":"Gimyo",
"회복 화분! HP +1":"Healing pot! HP +1",
"회복 화분을 찾았지만 HP가 가득 찼습니다.":"You found a healing pot, but your HP is already full.",
"화분 폭발!":"Pot exploded!",
"화분 회복!":"Healing pot!",
"화분 풀충전!":"Pots refilled!",
"필드 화분 리셋!":"Field pots reset!",
"감 과장 명중!":"Manager Gam hit!",
"방향 패드를 눌러 이동 · 누르고 있으면 계속 이동":"Press the directional pad to move · Hold to keep moving",
"방향 패드를 눌러 이동":"Press the directional pad to move",
"화면을 원하는 방향으로 밀기: 누르고 있으면 계속 이동":"Press the directional pad to move · Hold to keep moving",
"감 과장 화분: 회복 · 피해 · 화분 충전 · 필드 초기화 중 하나 · 대시 재사용: 기묘 3초 / 크다 5초 · 방향 패드를 눌러 이동":"Manager Gam's pot: one of heal, damage, refill, or field reset · Dash cooldown: Gimyo 3s / Keuda 5s · Press the directional pad to move",
"? 화분 4종":"4 random pot effects",
"하트 ±1":"±1 heart",
"화분 풀충전":"refill pots",
"필드 리셋":"reset the field",
"각 25%":"25% each",
"기묘: 대시 3초":"Gimyo: 3s dash",
"크다: 대시 5초":"Keuda: 5s dash",
"화면을 밀어 방향 조작":"Use the directional pad",
"누르고 있으면 계속 이동":"Hold to keep moving",
"? 화분 폭발!":"Mystery pot exploded!",
"? 화분 회복!":"Mystery pot restored HP!",
"? 화분 풀충전!":"Mystery pot refilled pots!",
"? 필드 화분 리셋!":"Mystery field pot reset!",
"감 과장 출동! ? 화분 투하!":"Manager Gam is here! Mystery pots incoming!",
"POT BREAKER RE 메인 화면":"POT BREAKER RE main screen",
"CBZP 사무실 배경의 POT BREAKER RE 메인 화면. 아래에는 뒤돌아선 기묘와 크다 부장이 보입니다.":"POT BREAKER RE's main screen with the CBZP office in the background; Gimyo and Manager Keuda are seen from behind below.",
"기묘와 크다 부장이 화분을 던지고 피하는 사무실 게임":"An office game where Gimyo and Manager Keuda throw and dodge flowerpots.",
"위로 이동":"Move up",
"왼쪽 이동":"Move left",
"오른쪽 이동":"Move right",
"아래로 이동":"Move down"
},
zh: {
"폿브레이커 RE | 기묘와 크다 부장의 사무실 미로":"POT BREAKER RE｜奇妙与克达部长",
"기묘와 크다 부장의 사무실 미로 추격전":"奇妙与克达部长的办公室迷宫追逐战",
"CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.":"扮演 CBZP 实习猫奇妙，在办公室迷宫中躲避克达部长并投掷花盆的单人网页游戏。",
"기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.":"免费浏览器迷宫游戏：操控奇妙在 CBZP 办公室中挑战克达部长。查看游戏介绍、操作、隐私与广告说明。",
"고양이 인턴 기묘와 악어 부장 크다의 CBZP 사무실 미로 추격전.":"猫咪实习生奇妙与鳄鱼部长克达在 CBZP 办公室迷宫展开追逐。",
"게임 시작":"开始游戏","🏆 랭킹":"🏆 排行榜","게임 방법":"游戏方法",
"방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.":"使用方向键移动、冲刺躲避，并投掷花盆。奇妙或克达部长任一方生命值归零时，比赛结束。",
"게임 소개와 조작법":"游戏介绍与操作","개인정보 및 광고 안내":"隐私与广告",
"이상한 회사의":"奇怪公司的","인턴 생활":"实习生活","정말... 이 회사에서":"真的……我能在这家公司","살아남을 수 있을까?":"活下来吗？",
"난이도":"难度","노멀":"普通","하드":"困难","베리 하드":"极难","사무실로 입장 ▶":"进入办公室 ▶",
"기묘 / PLAYER":"奇妙 / 玩家","크다 부장 / NPC":"克达部长 / NPC","대시":"冲刺","던지기":"投掷",
"↻ 다시 도전":"↻ 再试一次","처음으로":"返回首页","랭킹 등록":"提交排行","🏆 POT BREAKER 랭킹":"🏆 POT BREAKER 排行榜",
"닉네임":"昵称","최대 16자":"最多16个字符","랭킹을 불러오는 중…":"正在加载排行榜…","사무실 문을 열고 있습니다":"正在打开办公室的门",
"Python 게임 엔진을 준비하고 있습니다.":"正在准备 Python 游戏引擎。","다시 시도하기":"重试","잠깐 휴식!":"休息一下！","계속하기":"继续",
"아직 등록된 클리어 기록이 없습니다.":"暂无通关记录。","랭킹을 불러오지 못했습니다.":"无法加载排行榜。",
"서버 연결에 실패했습니다.":"连接服务器失败。","랭킹에 등록했습니다.":"已提交排行。","Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.":"无法加载 Pyodide，请检查网络连接。",
"게임 엔진을 불러오지 못했습니다.":"无法加载游戏引擎。","게임을 불러오지 못했습니다.":"无法加载游戏。","게임 화면 갱신 오류:":"游戏画面更新错误：",
"기묘 승리!":"奇妙获胜！","크다 부장 승리!":"克达部长获胜！","화분 한 방! 크다 부장의 뚝배기를 깼습니다.":"花盆一击！克达部长被击倒了。",
"기묘가 화분에 머리만 내놓고 심어졌습니다…":"奇妙被种进花盆，只露出了脑袋……","쨍그랑!":"哐当！","감 과장":"甘科长",
"랭킹 닫기":"关闭排行榜",
"♥ 회복 · 감 과장: ? 화분 4종 (하트 ±1 · 화분 풀충전 · 필드 리셋, 각 25%) · 기묘: 대시 3초 / 크다: 대시 5초 · 원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"♥ 回复 · 甘科长：4种随机花盆效果（心值±1、花盆补满、重置场地，各25%）· 奇妙冲刺：3秒 / 克达冲刺：5秒 · 使用圆形方向键移动，按住可持续移动",
"원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"使用圆形方向键移动 · 按住可持续移动","화분: 공격 · 대시 버튼: 3칸 돌진 (3초 재사용)":"花盆：攻击 · 冲刺：移动3格（冷却3秒）",
"PC: 방향키 / WASD · Space(공격) · Shift(대시)":"电脑：方向键 / WASD · 空格（投掷）· Shift（冲刺）",
"언어 변경":"切换语言","언어 선택":"选择语言","게임 안내":"游戏说明","기묘가 CBZP에 출근하고, 이상한 사무실에서 화분을 피하고 크다 부장에게 쫓기는 4컷 만화":"四格漫画：奇妙来到 CBZP 实习，在办公室躲避花盆并被克达部长追赶。",
"대시 버튼: 3칸 돌진 · 3초 재사용 대기":"冲刺：移动3格 · 冷却3秒",
"감 과장 출동!":"甘科长登场！",
"화분 투하!":"花盆来袭！",
"크다":"克达",
"기묘":"奇妙",
"회복 화분! HP +1":"恢复花盆！HP +1",
"회복 화분을 찾았지만 HP가 가득 찼습니다.":"找到了恢复花盆，但生命值已满。",
"화분 폭발!":"花盆爆炸！",
"화분 회복!":"花盆恢复！",
"화분 풀충전!":"花盆补满！",
"필드 화분 리셋!":"场地花盆已重置！",
"감 과장 명중!":"甘科长命中！",
"방향 패드를 눌러 이동 · 누르고 있으면 계속 이동":"按方向键移动 · 按住可持续移动",
"방향 패드를 눌러 이동":"按方向键移动",
"화면을 원하는 방향으로 밀기: 누르고 있으면 계속 이동":"按方向键移动 · 按住可持续移动",
"감 과장 화분: 회복 · 피해 · 화분 충전 · 필드 초기화 중 하나 · 대시 재사용: 기묘 3초 / 크다 5초 · 방향 패드를 눌러 이동":"甘科长花盆效果随机一种：恢复、受伤、补充花盆或重置场地 · 冲刺冷却：奇妙3秒 / 克达5秒 · 按方向键移动",
"? 화분 4종":"4种随机花盆效果",
"하트 ±1":"心值±1",
"화분 풀충전":"花盆补满",
"필드 리셋":"重置场地",
"각 25%":"各25%",
"기묘: 대시 3초":"奇妙：冲刺3秒",
"크다: 대시 5초":"克达：冲刺5秒",
"화면을 밀어 방향 조작":"按方向键移动",
"누르고 있으면 계속 이동":"按住可持续移动",
"? 화분 폭발!":"神秘花盆爆炸！",
"? 화분 회복!":"神秘花盆恢复！",
"? 화분 풀충전!":"神秘花盆补满！",
"? 필드 화분 리셋!":"神秘花盆重置场地！",
"감 과장 출동! ? 화분 투하!":"甘科长来了！神秘花盆掉落！",
"POT BREAKER RE 메인 화면":"POT BREAKER RE 主画面",
"CBZP 사무실 배경의 POT BREAKER RE 메인 화면. 아래에는 뒤돌아선 기묘와 크다 부장이 보입니다.":"POT BREAKER RE 主画面以 CBZP 办公室为背景，下方可见奇妙和克达部长的背影。",
"기묘와 크다 부장이 화분을 던지고 피하는 사무실 게임":"奇妙与克达部长在办公室里投掷并躲避花盆的游戏。",
"위로 이동":"向上移动",
"왼쪽 이동":"向左移动",
"오른쪽 이동":"向右移动",
"아래로 이동":"向下移动"
},
ja: {
"폿브레이커 RE | 기묘와 크다 부장의 사무실 미로":"POT BREAKER RE｜キミョとクダ部長",
"기묘와 크다 부장의 사무실 미로 추격전":"キミョとクダ部長のオフィス迷路チェイス",
"CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.":"CBZPの猫インターン、キミョを操作して、オフィス迷路でクダ部長を避けながら植木鉢を投げるブラウザーゲームです。",
"기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.":"キミョを操作してCBZPのオフィス迷路でクダ部長と対決する無料ブラウザーゲーム。遊び方、操作方法、プライバシーと広告の案内はこちら。",
"고양이 인턴 기묘와 악어 부장 크다의 CBZP 사무실 미로 추격전.":"猫のインターン、キミョとワニのクダ部長がCBZPのオフィス迷路で追いかけっこ。",
"게임 시작":"ゲーム開始","🏆 랭킹":"🏆 ランキング","게임 방법":"遊び方",
"방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.":"方向パッドで移動し、ダッシュで攻撃を避け、投げるボタンで植木鉢を投げます。どちらかの体力が0になると試合終了です。",
"게임 소개와 조작법":"ゲーム紹介・操作方法","개인정보 및 광고 안내":"プライバシー・広告について",
"이상한 회사의":"不思議な会社の","인턴 생활":"インターン生活","정말... 이 회사에서":"本当に…この会社で","살아남을 수 있을까?":"生き残れるのかな？",
"난이도":"難易度","노멀":"ノーマル","하드":"ハード","베리 하드":"ベリーハード","사무실로 입장 ▶":"オフィスへ ▶",
"기묘 / PLAYER":"キミョ / PLAYER","크다 부장 / NPC":"クダ部長 / NPC","대시":"ダッシュ","던지기":"投げる",
"↻ 다시 도전":"↻ もう一度挑戦","처음으로":"タイトルへ","랭킹 등록":"ランキング登録","🏆 POT BREAKER 랭킹":"🏆 POT BREAKER ランキング",
"닉네임":"ニックネーム","최대 16자":"16文字まで","랭킹을 불러오는 중…":"ランキングを読み込み中…","사무실 문을 열고 있습니다":"オフィスのドアを開いています",
"Python 게임 엔진을 준비하고 있습니다.":"Pythonゲームエンジンを準備しています。","다시 시도하기":"再試行","잠깐 휴식!":"ちょっと休憩！","계속하기":"続ける",
"아직 등록된 클리어 기록이 없습니다.":"クリア記録はまだありません。","랭킹을 불러오지 못했습니다.":"ランキングを読み込めませんでした。",
"서버 연결에 실패했습니다.":"サーバーに接続できませんでした。","랭킹에 등록했습니다.":"ランキングに登録しました。","Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.":"Pyodideを読み込めませんでした。ネット接続を確認してください。",
"게임 엔진을 불러오지 못했습니다.":"ゲームエンジンを読み込めませんでした。","게임을 불러오지 못했습니다.":"ゲームを読み込めませんでした。","게임 화면 갱신 오류:":"画面更新エラー：",
"기묘 승리!":"キミョの勝利！","크다 부장 승리!":"クダ部長の勝利！","화분 한 방! 크다 부장의 뚝배기를 깼습니다.":"植木鉢の一撃！クダ部長を倒しました。",
"기묘가 화분에 머리만 내놓고 심어졌습니다…":"キミョは植木鉢に植えられ、頭だけ出ています…","쨍그랑!":"ガシャーン！","감 과장":"カム課長",
"랭킹 닫기":"ランキングを閉じる",
"♥ 회복 · 감 과장: ? 화분 4종 (하트 ±1 · 화분 풀충전 · 필드 리셋, 각 25%) · 기묘: 대시 3초 / 크다: 대시 5초 · 원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"♥ 回復 · カム課長：植木鉢の効果4種（ハート±1、植木鉢補充、フィールドリセット・各25%）· キミョのダッシュ：3秒 / クダのダッシュ：5秒 · 円形パッドで移動、長押しで連続移動",
"원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"円形パッドで移動 · 長押しで連続移動","화분: 공격 · 대시 버튼: 3칸 돌진 (3초 재사용)":"植木鉢：攻撃 · ダッシュ：3マス移動（クールダウン3秒）",
"PC: 방향키 / WASD · Space(공격) · Shift(대시)":"PC：矢印キー / WASD · Space（投げる）· Shift（ダッシュ）",
"언어 변경":"言語を変更","언어 선택":"言語を選択","게임 안내":"ゲームガイド","기묘가 CBZP에 출근하고, 이상한 사무실에서 화분을 피하고 크다 부장에게 쫓기는 4컷 만화":"4コマ漫画：キミョがCBZPに出勤し、植木鉢を避けながらクダ部長に追われます。",
"대시 버튼: 3칸 돌진 · 3초 재사용 대기":"ダッシュ：3マス移動 · クールダウン3秒",
"감 과장 출동!":"カム課長が登場！",
"화분 투하!":"植木鉢が降ってくる！",
"크다":"クダ",
"기묘":"キミョ",
"회복 화분! HP +1":"回復の植木鉢！HP +1",
"회복 화분을 찾았지만 HP가 가득 찼습니다.":"回復の植木鉢を見つけましたが、HPは満タンです。",
"화분 폭발!":"植木鉢が爆発！",
"화분 회복!":"植木鉢で回復！",
"화분 풀충전!":"植木鉢を補充！",
"필드 화분 리셋!":"フィールドの植木鉢をリセット！",
"감 과장 명중!":"カム課長に命中！",
"방향 패드를 눌러 이동 · 누르고 있으면 계속 이동":"方向パッドで移動 · 長押しで連続移動",
"방향 패드를 눌러 이동":"方向パッドで移動",
"화면을 원하는 방향으로 밀기: 누르고 있으면 계속 이동":"方向パッドで移動 · 長押しで連続移動",
"감 과장 화분: 회복 · 피해 · 화분 충전 · 필드 초기화 중 하나 · 대시 재사용: 기묘 3초 / 크다 5초 · 방향 패드를 눌러 이동":"カム課長の植木鉢：回復・ダメージ・補充・フィールド初期化のいずれか · ダッシュ待機：キミョ3秒 / クダ5秒 · 方向パッドで移動",
"? 화분 4종":"植木鉢の効果は4種類",
"하트 ±1":"ハート±1",
"화분 풀충전":"植木鉢を補充",
"필드 리셋":"フィールド初期化",
"각 25%":"各25%",
"기묘: 대시 3초":"キミョ：ダッシュ3秒",
"크다: 대시 5초":"クダ：ダッシュ5秒",
"화면을 밀어 방향 조작":"方向パッドで移動",
"누르고 있으면 계속 이동":"長押しで連続移動",
"? 화분 폭발!":"謎の植木鉢が爆発！",
"? 화분 회복!":"謎の植木鉢で回復！",
"? 화분 풀충전!":"謎の植木鉢を補充！",
"? 필드 화분 리셋!":"謎の植木鉢でフィールドを初期化！",
"감 과장 출동! ? 화분 투하!":"カム課長が登場！謎の植木鉢が降ってくる！",
"POT BREAKER RE 메인 화면":"POT BREAKER RE メイン画面",
"CBZP 사무실 배경의 POT BREAKER RE 메인 화면. 아래에는 뒤돌아선 기묘와 크다 부장이 보입니다.":"CBZPオフィスを背景にしたPOT BREAKER REのメイン画面。下には後ろ姿のキミョとクダ部長が見えます。",
"기묘와 크다 부장이 화분을 던지고 피하는 사무실 게임":"キミョとクダ部長がオフィスで植木鉢を投げ合い、避けるゲームです。",
"위로 이동":"上へ移動",
"왼쪽 이동":"左へ移動",
"오른쪽 이동":"右へ移動",
"아래로 이동":"下へ移動"
}
};
const selectors=[...document.querySelectorAll(".locale-control select")];
if(!selectors.length)return;
const textOriginal=new WeakMap(),textRendered=new WeakMap(),attrOriginal=new WeakMap(),attrRendered=new WeakMap();
const routeLocale=location.pathname.match(/^\/(en|zh|ja)\/?$/)?.[1];
let locale=routeLocale||"ko",busy=false;
if(!routeLocale){try{const saved=localStorage.getItem("potbreaker-locale");if(["ko","en","zh","ja"].includes(saved))locale=saved}catch{}}
const translateNotice=value=>{
 const names=locale==="en"?{"기묘":"Gimyo","크다":"Keuda"}:locale==="zh"?{"기묘":"奇妙","크다":"克达"}:{"기묘":"キミョ","크다":"クダ"};
 let m=value.match(/^\? 화분 (폭발|회복)! (기묘|크다) HP ([+-]1)$/);
 if(m){
  const name=names[m[2]],amount=m[3];
  if(locale==="en")return m[1]==="폭발"?"Mystery pot exploded! "+name+" HP "+amount:"Mystery pot restored "+name+"'s HP "+amount;
  if(locale==="zh")return m[1]==="폭발"?"神秘花盆爆炸！"+name+" HP "+amount:"神秘花盆恢复！"+name+" HP "+amount;
  return m[1]==="폭발"?"謎の植木鉢が爆発！"+name+" HP "+amount:"謎の植木鉢で"+name+"のHPが"+amount+"回復！";
 }
 m=value.match(/^\? 화분 풀충전! (기묘|크다) 화분 (\d+\/\d+)$/);
 if(m){
  const name=names[m[1]],count=m[2];
  if(locale==="en")return "Mystery pot refilled "+name+"'s pots ("+count+")";
  if(locale==="zh")return "神秘花盆补满"+name+"的花盆（"+count+"）";
  return "謎の植木鉢で"+name+"の植木鉢を補充（"+count+"）";
 }
 if(value==="? 필드 화분 리셋!"){
  return locale==="en"?"Mystery pot reset the field!":locale==="zh"?"神秘花盆重置了场地！":"謎の植木鉢でフィールドをリセット！";
 }
 m=value.match(/^감 과장 명중! (기묘) HP \+1$/);
 if(m)return locale==="en"?"Manager Gam hit! Gimyo HP +1":locale==="zh"?"甘科长命中！奇妙 HP +1":"カム課長に命中！キミョ HP +1";
 m=value.match(/^(기묘|크다) 회복 화분! HP \+1$/);
 if(m){
  const name=names[m[1]];
  return locale==="en"?name+" healed! HP +1":locale==="zh"?name+"恢复了！HP +1":name+"が回復！HP +1";
 }
 return null;
};
const translate=value=>{
 if(locale==="ko")return value;
 const notice=translateNotice(value);if(notice!==null)return notice;
 const dictionary=dictionaries[locale]||{};
 if(Object.prototype.hasOwnProperty.call(dictionary,value))return dictionary[value];
 let result=value;
 for(const key of Object.keys(dictionary).sort((a,b)=>b.length-a.length)){
  if(result.includes(key))result=result.split(key).join(dictionary[key]);
 }
 return result;
};
const visitTextNode=n=>{
 const current=n.nodeValue;
 if(!textOriginal.has(n)||(textRendered.has(n)&&textRendered.get(n)!==current))textOriginal.set(n,current);
 const next=translate(textOriginal.get(n));textRendered.set(n,next);
 if(next!==current)n.nodeValue=next;
};
function visit(root=document.documentElement){
 if(!root)return;
 if(root.nodeType===Node.TEXT_NODE){
  if(!root.parentElement?.closest("script,style,select,option,textarea"))visitTextNode(root);
  return;
 }
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement?.closest("script,style,select,option,textarea")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
 let n;while(n=walker.nextNode())visitTextNode(n);
 const elements=root.nodeType===Node.ELEMENT_NODE?[root,...root.querySelectorAll("*")]:[];
 const attrs=["aria-label","title","placeholder","content"];
 for(const el of elements){
  let saved=attrOriginal.get(el);if(!saved){saved={};attrOriginal.set(el,saved)}
  for(const attr of attrs){if(!el.hasAttribute(attr))continue;
   const current=el.getAttribute(attr),key=attr+":"+el.tagName,rendered=attrRendered.get(el)||{};
   if(!Object.prototype.hasOwnProperty.call(saved,key)||(Object.prototype.hasOwnProperty.call(rendered,key)&&rendered[key]!==current))saved[key]=current;
   const next=translate(saved[key]);rendered[key]=next;attrRendered.set(el,rendered);
   if(next!==current)el.setAttribute(attr,next)
  }
 }
}
const comicCaptions={
en:["Gimyo starts as a CBZP intern!","But… something feels strange about the office.","A flowerpot suddenly flies in from somewhere!","Manager Keuda throws another flowerpot at Gimyo!","Whoosh!"],
zh:["奇妙来到 CBZP，开始实习了！","但是……公司的气氛有点奇怪。","突然，不知从哪儿飞来了花盆！","克达部长又朝奇妙扔花盆了！","嗖！"],
ja:["キミョ、CBZPでインターン開始！","でも…会社の雰囲気がなんだか変。","突然どこからか植木鉢が飛んできた！","クダ部長がキミョにまた植木鉢を投げた！","シュッ！"]
};
const localizedComicImages={
ko:"https://raw.githubusercontent.com/rhaxod7784-png/potbreaker/feat/potbreaker-seo-adsense/web/assets/comic-ko.png",
en:"https://raw.githubusercontent.com/rhaxod7784-png/potbreaker/feat/potbreaker-seo-adsense/web/assets/comic-en.png",
zh:"https://raw.githubusercontent.com/rhaxod7784-png/potbreaker/feat/potbreaker-seo-adsense/web/assets/comic-zh.png",
ja:"https://raw.githubusercontent.com/rhaxod7784-png/potbreaker/feat/potbreaker-seo-adsense/web/assets/comic-ja.png"
};
function drawComicTranslations(){
 const img=document.querySelector(".comic-cover");if(!img)return;
 if(img.dataset.pbLocalizedComic==="true"){
  img.parentElement?.querySelector(".comic-translation-layer")?.remove();
  return;
 }
 let wrap=img.parentElement;
 if(!wrap?.classList.contains("comic-cover-wrap")){
  wrap=document.createElement("div");wrap.className="comic-cover-wrap";
  img.parentNode.insertBefore(wrap,img);wrap.appendChild(img);
 }
 let canvas=wrap.querySelector(".comic-translation-layer");
 if(!canvas){canvas=document.createElement("canvas");canvas.className="comic-translation-layer";canvas.setAttribute("aria-hidden","true");wrap.appendChild(canvas)}
 const draw=()=>{
  const wr=wrap.getBoundingClientRect(),ir=img.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
  if(!wr.width||!wr.height||!ir.width||!ir.height||!img.naturalWidth||!img.naturalHeight)return;
  canvas.width=Math.round(wr.width*dpr);canvas.height=Math.round(wr.height*dpr);
  const ctx=canvas.getContext("2d");ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,wr.width,wr.height);
  if(locale==="ko")return;
  const captions=comicCaptions[locale];if(!captions)return;
  const fit=Math.min(ir.width/img.naturalWidth,ir.height/img.naturalHeight);
  const contentW=img.naturalWidth*fit,contentH=img.naturalHeight*fit;
  const contentX=ir.left-wr.left+(ir.width-contentW)/2,contentY=ir.top-wr.top+(ir.height-contentH)/2;
  const boxes=[
   {x:.073,y:.177,w:.31,h:.061},{x:.548,y:.177,w:.37,h:.061},
   {x:.073,y:.56,w:.41,h:.085},{x:.582,y:.54,w:.395,h:.085}
  ];
  boxes.forEach((box,index)=>{
   const x=contentX+contentW*box.x,y=contentY+contentH*box.y,w=contentW*box.w,h=contentH*box.h,r=Math.min(5,h*.16);
   ctx.beginPath();if(ctx.roundRect)ctx.roundRect(x,y,w,h,r);else ctx.rect(x,y,w,h);
   ctx.fillStyle="#fffdf5";ctx.fill();ctx.strokeStyle="#d4d0c8";ctx.lineWidth=Math.max(1,h*.025);ctx.stroke();
   let size=h*.48;ctx.font="800 "+size+"px system-ui,'Noto Sans CJK KR',sans-serif";
   while(ctx.measureText(captions[index]).width>w-10&&size>h*.25){size-=.5;ctx.font="800 "+size+"px system-ui,'Noto Sans CJK KR',sans-serif"}
   ctx.fillStyle="#203451";ctx.textAlign="left";ctx.textBaseline="middle";
   ctx.fillText(captions[index],x+5,y+h*.52,w-10);
  });
  const effect=captions[4];
  if(effect){
   const x=contentX+contentW*.135,y=contentY+contentH*.625,w=contentW*.135,h=contentH*.13;
   ctx.beginPath();if(ctx.roundRect)ctx.roundRect(x,y,w,h,Math.min(8,h*.16));else ctx.rect(x,y,w,h);
   ctx.fillStyle="rgba(255,253,245,.94)";ctx.fill();
   ctx.font="1000 "+Math.min(h*.46,w*.22)+"px system-ui,sans-serif";
   ctx.fillStyle="#23427a";ctx.textAlign="center";ctx.textBaseline="middle";
   ctx.fillText(effect,x+w/2,y+h/2,w-8);
  }
 };
 if(img.complete)draw();else img.addEventListener("load",draw,{once:true});
 if(!canvas.__pbResizeObserver){canvas.__pbResizeObserver=new ResizeObserver(draw);canvas.__pbResizeObserver.observe(wrap);canvas.__pbResizeObserver.observe(img)}
 window.addEventListener("resize",draw,{passive:true});
}

function drawEndingTranslations(){
 const end=document.querySelector("#end"),img=document.querySelector("#endingArt");if(!end||!img)return;
 let canvas=end.querySelector(".ending-translation-layer");
 if(!canvas){
  canvas=document.createElement("canvas");canvas.className="ending-translation-layer";canvas.setAttribute("aria-hidden","true");
  canvas.style.cssText="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1";
  end.appendChild(canvas);
 }
 const draw=()=>{
  const er=end.getBoundingClientRect(),ir=img.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
  if(!er.width||!er.height||!ir.width||!ir.height||!img.naturalWidth||!img.naturalHeight)return;
  canvas.width=Math.round(er.width*dpr);canvas.height=Math.round(er.height*dpr);
  const ctx=canvas.getContext("2d");ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,er.width,er.height);
  const tag=document.querySelector("#endTag");
  if(locale==="ko"||!tag?.textContent.includes("WINNER"))return;
  const fit=Math.max(ir.width/img.naturalWidth,ir.height/img.naturalHeight);
  const contentW=img.naturalWidth*fit,contentH=img.naturalHeight*fit;
  const contentX=ir.left-er.left+(ir.width-contentW)/2,contentY=ir.top-er.top+(ir.height-contentH)/2;
  const captions=locale==="en"?{title:"GIMYO WINS!",impact:"BAM!"}:locale==="zh"?{title:"奇妙获胜！",impact:"砰！"}:{title:"キミョの勝利！",impact:"ドカン！"};
  const cover=(box,stroke)=>{
   const x=contentX+contentW*box.x,y=contentY+contentH*box.y,w=contentW*box.w,h=contentH*box.h,r=Math.min(h*.2,22);
   ctx.beginPath();if(ctx.roundRect)ctx.roundRect(x,y,w,h,r);else ctx.rect(x,y,w,h);
   ctx.fillStyle="#fffaf0";ctx.fill();ctx.lineWidth=Math.max(2,h*.025);ctx.strokeStyle=stroke;ctx.stroke();
   return {x,y,w,h};
  };
  const heading=cover({x:.03,y:.035,w:.47,h:.315},"#e7ad47");
  ctx.textAlign="center";ctx.textBaseline="middle";ctx.lineJoin="round";
  let size=Math.min(heading.h*.34,heading.w*.11);
  ctx.font="1000 "+size+"px system-ui,'Noto Sans CJK KR',sans-serif";
  while(ctx.measureText(captions.title).width>heading.w-24&&size>heading.h*.22){size-=2;ctx.font="1000 "+size+"px system-ui,'Noto Sans CJK KR',sans-serif"}
  ctx.lineWidth=Math.max(3,size*.08);ctx.strokeStyle="#e4a63e";ctx.strokeText(captions.title,heading.x+heading.w/2,heading.y+heading.h/2,heading.w-24);
  ctx.fillStyle="#243c72";ctx.fillText(captions.title,heading.x+heading.w/2,heading.y+heading.h/2,heading.w-24);
  const impact=cover({x:.765,y:.12,w:.17,h:.18},"#405b9a");
  size=Math.min(impact.h*.48,impact.w*.25);ctx.font="1000 "+size+"px system-ui,sans-serif";
  ctx.lineWidth=Math.max(2,size*.06);ctx.strokeStyle="#e9aa37";ctx.strokeText(captions.impact,impact.x+impact.w/2,impact.y+impact.h/2,impact.w-12);
  ctx.fillStyle="#24427d";ctx.fillText(captions.impact,impact.x+impact.w/2,impact.y+impact.h/2,impact.w-12);
 };
 if(!canvas.__pbEndingObserver){
  img.addEventListener("load",draw);
  const observer=new ResizeObserver(draw);observer.observe(end);observer.observe(img);canvas.__pbEndingObserver=observer;
 }
 draw();
}

function apply(next){
 locale=["ko","en","zh","ja"].includes(next)?next:"ko";
 try{localStorage.setItem("potbreaker-locale",locale)}catch{}
 document.documentElement.lang=locale;
 const localePath=locale==="ko"?"/":"/"+locale;
 if(location.pathname!==localePath)history.replaceState(null,"",localePath+location.search+location.hash);
 const canonical=document.querySelector('link[rel="canonical"]');if(canonical)canonical.href=location.origin+localePath;
 const ogLocale=document.querySelector('meta[property="og:locale"]');if(ogLocale)ogLocale.content=locale==="ko"?"ko_KR":locale==="en"?"en_US":locale==="zh"?"zh_CN":"ja_JP";
 busy=true;selectors.forEach(selector=>selector.value=locale);
 const comicImg=document.querySelector(".comic-cover"),comicUrl=localizedComicImages[locale];
 if(comicImg&&comicUrl&&comicImg.dataset.pbComicLocale!==locale){
  comicImg.dataset.pbLocalizedComic="true";
  comicImg.dataset.pbComicLocale=locale;
  comicImg.src=comicUrl;
  comicImg.alt=locale==="en"?"Four-panel POT BREAKER RE comic, English edition":locale==="zh"?"POT BREAKER RE 四格漫画，简体中文版":locale==="ja"?"POT BREAKER REの4コマ漫画、日本語版":"폿브레이커 RE 4컷 만화, 한국어 버전";
 }
 document.querySelectorAll('a[href="/about"],a[href="/privacy"]').forEach(link=>{const slug=link.getAttribute("href").slice(1);link.href=locale==="ko"?"/"+slug:"/"+locale+"/"+slug});
 visit();drawComicTranslations();drawEndingTranslations();busy=false;
}
selectors.forEach(selector=>selector.addEventListener("change",()=>apply(selector.value)));
window.addEventListener("popstate",()=>apply(location.pathname.match(/^\/(en|zh|ja)\/?$/)?.[1]||"ko"));
if(window.CanvasRenderingContext2D&&!CanvasRenderingContext2D.prototype.__pbTranslated){
 for(const method of ["fillText","strokeText"]){
  const original=CanvasRenderingContext2D.prototype[method];
  CanvasRenderingContext2D.prototype[method]=function(text,...args){return original.call(this,translate(String(text)),...args)};
 }
 CanvasRenderingContext2D.prototype.__pbTranslated=true;
}
apply(locale);
new MutationObserver(records=>{
 if(busy)return;
 let redrawComic=false,redrawEnding=false;
 for(const r of records){
  const target=r.target,el=target.nodeType===Node.ELEMENT_NODE?target:target.parentElement;
  if(r.type==="characterData"){
   visit(target);
   if(el?.closest("#end"))redrawEnding=true;
  }else if(r.type==="childList"){
   for(const node of r.addedNodes)if(node.nodeType===Node.ELEMENT_NODE||node.nodeType===Node.TEXT_NODE)visit(node);
   if(el?.closest("#intro"))redrawComic=true;
   if(el?.closest("#end"))redrawEnding=true;
  }else if(r.type==="attributes"){
   visit(target);
   if(target.matches?.("#intro")||target.closest?.("#intro"))redrawComic=true;
   if(target.matches?.("#end")||target.closest?.("#end"))redrawEnding=true;
  }
 }
 if(redrawComic)requestAnimationFrame(drawComicTranslations);
 if(redrawEnding)requestAnimationFrame(drawEndingTranslations);
}).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:["aria-label","title","placeholder","content","src","class"]});
})();