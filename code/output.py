path = r"C:\Users\User\Documents\GitHub\project_temp-a\repo\a.txt"

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

paragraphs = text.split("--")

bolds = text.split("*")


# 앞뒤 공백 제거
paragraphs = [p.strip() for p in paragraphs]
paragraphs = [p.strip() for p in paragraphs]

# 원하는 문단 번호, 예: 1번째 문단
index = 1

print("pa",paragraphs[index - 1])
print("pa",paragraphs[index - 1])