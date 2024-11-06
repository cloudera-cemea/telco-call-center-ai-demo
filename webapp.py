from flask import Flask, render_template
import os

PORT = os.getenv('CDSW_APP_PORT', '8090')

context = {
  "AI_MODEL_ACCESS_KEY": os.getenv("AI_MODEL_ACCESS_KEY"),
  "SENTIMENT_MODEL_ACCESS_KEY": os.getenv("SENTIMENT_MODEL_ACCESS_KEY")  
}

app = Flask(__name__)

@app.route("/")
def main():
  return render_template('frontend.html', **context)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=PORT)
