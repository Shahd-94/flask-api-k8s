from flask_cors import CORS
from flask import Flask, Response, jsonify
from github import Github
from dotenv import load_dotenv
import os
from prometheus_client import generate_latest, Counter, Gauge, CollectorRegistry

app = Flask(__name__)
CORS(app)
load_dotenv()

access_token = os.environ.get("TOKEN")

# Prometheus metrics
registry = CollectorRegistry()
REPO_COUNT = Gauge('github_repo_count', 'Number of public repositories owned by the user', registry=registry)

@app.route('/create/<string:name>', methods=['GET'])
def create(name):
    try:
        g = Github(access_token)
        user = g.get_user()
        repo = user.create_repo(name=name, private=False)

        # Calling create_readme function
        create_readme(repo, name)

        # Update metrics
        update_repo_count(user)

        return jsonify(message=f"Successfully created repository {name} and a base README file in it")
    except Exception as e:
        return jsonify(error=str(e)), 500

def update_repo_count(user):
    try:
        repo_count = len(list(user.get_repos(visibility="public")))
        REPO_COUNT.set(repo_count)
    except Exception as e:
        print(f"Error updating repo count metric: {str(e)}")

@app.route('/metrics', methods=['GET'])
def metrics():
    # Expose Prometheus metrics
    try:
        return Response(generate_latest(registry), mimetype='text/plain')
    except Exception as e:
        return jsonify(error=f"Error generating metrics: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=False)

def create_readme(repo, name):
    try:
        content = f"""# {name} Repository\n\nThis is a basic README file for the repository.\n\n## Overview\nThis repository was created using the GitHub API.\n\n## Features\n- Automatically generated repository\n- Initial README file with basic content\n\n## Usage\nFeel free to add more content and customize it as needed.\n"""
        repo.create_file("README.md", "Initial commit with README", content)
        print(f"Successfully created README file in repository: {name}")
    except Exception as e:
        print(f"Error creating README file: {str(e)}")
