import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from bs4 import BeautifulSoup
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/c')
def c():
    return send_from_directory('.', 'c.html')


@app.route('/repo/<path:filename>')
def repo_file(filename):
    return send_from_directory('repo', filename)


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    if not data or not data.get('html', '').strip():
        return jsonify({'error': 'HTML 내용을 입력해주세요.'}), 400

    soup = BeautifulSoup(data['html'], 'html.parser')
    for tag in soup(['script', 'style', 'meta', 'link', 'noscript', 'head']):
        tag.decompose()

    text = soup.get_text(separator='\n', strip=True)
    text = '\n'.join(line for line in text.splitlines() if line.strip())

    if len(text.strip()) < 20:
        return jsonify({'error': '분석할 텍스트 내용이 너무 짧습니다.'}), 400

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=(
                "당신은 텍스트 요약 및 키워드 추출 전문가입니다. "
                "입력된 텍스트의 언어(한국어/영어 등)에 맞게 분석 결과를 반환하세요."
            ),
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "5~10개의 핵심 키워드"
                            },
                            "summary": {
                                "type": "string",
                                "description": "전체 내용을 3~5문장으로 요약"
                            },
                            "key_points": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "3~5개의 주요 포인트"
                            }
                        },
                        "required": ["keywords", "summary", "key_points"],
                        "additionalProperties": False
                    }
                }
            },
            messages=[{
                "role": "user",
                "content": "다음 텍스트를 분석해주세요:\n\n" + text[:8000]
            }]
        )

        for block in response.content:
            if block.type == 'text':
                return jsonify(json.loads(block.text))

        return jsonify({'error': '결과를 가져올 수 없습니다.'}), 500

    except anthropic.AuthenticationError:
        return jsonify({'error': 'API 키가 올바르지 않습니다. ANTHROPIC_API_KEY를 확인해주세요.'}), 401
    except anthropic.RateLimitError:
        return jsonify({'error': '요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.'}), 429
    except anthropic.APIConnectionError:
        return jsonify({'error': '네트워크 연결 오류입니다.'}), 503
    except Exception as e:
        app.logger.error(f"Summarize error: {e}")
        return jsonify({'error': '분석 중 오류가 발생했습니다.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
