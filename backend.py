import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# 감정-장르 맵핑
# -----------------------------
emotion_genre_map = {
    "happy": ["Pop","Indie Pop","Synthpop","Dance Pop","Electropop","Hyperpop","Teen Pop",
              "Funk","Disco","EDM","House","Trance","Latin","Reggaeton","Salsa","Bossa Nova",
              "Electro Swing","Deep House"],
    "sad": ["Ballad","Blues","Neo Soul","R&B","Soul","Acoustic","Folk","Indie Folk",
            "Piano","Classical","Soundtrack","Baroque"],
    "relaxed": ["Lo-fi Hip Hop","Chillout","Ambient","Jazz","Vocal Jazz","New Age","World Fusion"],
    "angry": ["Rock","Alternative Rock","Hard Rock","Classic Rock","Indie Rock","Punk Rock",
              "Grunge","Metal","Heavy Metal","Rap","Trap","Hip Hop","Drill","Techno","Dubstep",
              "Drum & Bass"],
    "focus": ["Experimental","Acoustic","Indie Folk","Piano","Classical"],
    "confident": ["Rock","Alternative Rock","Indie Rock","Hip Hop","Rap","Trap",
                  "EDM","Funk","Electro Swing","House"]
}
emotions = list(emotion_genre_map.keys())


# -----------------------------
# CSV 읽기
# -----------------------------
# CSV 컬럼 구조 가정:
# 0: genre
# 1: title
# 2: artist
# 3: (unused)
# 4: popularity
# 5: spotify_url ★ 반드시 존재해야 함!
music_df = pd.read_csv("music.csv", header=None)

# spotify_url 포함해서 불러오기
music_df = music_df[[0,1,2,4,5]]
music_df.columns = ["genre","title","artist","popularity","spotify_url"]

# 숫자로 변환
music_df["popularity"] = pd.to_numeric(music_df["popularity"], errors='coerce')
music_df = music_df.dropna(subset=["popularity"]).copy()


# -----------------------------
# 인기도 레벨 매핑
# -----------------------------
def map_popularity(pop):
    if 60 <= pop <= 70: return 0
    elif 71 <= pop <= 80: return 1
    elif 81 <= pop <= 99: return 2
    else: return 0

music_df['pop_level'] = music_df['popularity'].apply(map_popularity)


# -----------------------------
# 장르별 감정 벡터
# -----------------------------
def genre_emotion_vector(genre):
    vec = [0]*len(emotions)
    for i,e in enumerate(emotions):
        if genre in emotion_genre_map[e]:
            vec[i] = 1
    return np.array(vec)

music_df['feature_vec'] = music_df.apply(
    lambda row: np.append(genre_emotion_vector(row['genre']), row['pop_level']),
    axis=1
)


# -----------------------------
# 사용자 feature vector
# -----------------------------
def user_vector(user_emotions, user_pop_level):
    return np.array([1 if e in user_emotions else 0 for e in emotions] + [user_pop_level])


# -----------------------------
# KNN 학습
# -----------------------------
X = np.stack(music_df['feature_vec'].values)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

knn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
knn_model.fit(X_scaled)


# -----------------------------
# 추천 함수 (Spotify URL 포함)
# -----------------------------
def recommend_knn(user_emotions, user_pop_level, top_k=3, candidate_pool=10):

    u_vec = user_vector(user_emotions, user_pop_level)
    u_scaled = scaler.transform([u_vec])

    dist, idx = knn_model.kneighbors(u_scaled, n_neighbors=candidate_pool)
    top_candidates = music_df.iloc[idx[0]]

    selected = top_candidates.sample(n=top_k)

    recommendations = []
    for _, row in selected.iterrows():
        sim = cosine_similarity([u_vec], [row['feature_vec']])[0][0]
        recommendations.append({
            "genre": row['genre'],
            "title": row['title'],
            "artist": row['artist'],
            "similarity": round(float(sim), 4),
            "spotify_url": row['spotify_url']   # ★ 추가됨!
        })

    return recommendations
