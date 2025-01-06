import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import pafy
import pkg_resources
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})

# @app.route('/')
# def index():
#     return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})
@app.route('/')
def index():
    # Get installed packages and versions
    installed_packages = [{"name": dist.project_name, "version": dist.version} for dist in pkg_resources.working_set]
    return jsonify({"dependencies": installed_packages})

@app.route('/api', methods=["POST"])
def api():
    vid_id = ""
    try:
        req_data = request.get_json()
        vid_url = req_data["url"]
        pafy_vid = pafy.new(vid_url)

        vid_duration = pafy_vid.duration
        vid_id = vid_url[32:]
        transcript_list = YouTubeTranscriptApi.list_transcripts(vid_id)
        transcript = transcript_list.find_generated_transcript(['en'])
        transcript = transcript.fetch()

        resp_data = {
            "state": "success",
            "id": vid_id,
            "duration": vid_duration,
            "transcript": transcript
        }
        return jsonify(resp_data)
    except Exception as e:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(vid_id)
            resp_data = {
                "state": "success",
                "id": vid_id,
                "duration": vid_duration,
                "transcript": transcript
            }
            return jsonify(resp_data)
        except Exception as inner_e:
            resp_data = {
                "state": "failed",
                "id": "",
                "duration": "",
                "transcript": None,
                "error": str(inner_e)  # Capture the inner exception details
            }
            return jsonify(resp_data), 400
    # req_data = request.get_json()
    # resp_data = {
    #     "status": "success",
    #     "url": req_data["url"]
    # }
    # return resp_data
    


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
