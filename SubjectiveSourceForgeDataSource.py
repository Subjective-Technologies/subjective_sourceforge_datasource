import os
import subprocess
import requests
from urllib.parse import urljoin

from subjective_abstract_data_source_package import SubjectiveDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class SubjectiveSourceForgeDataSource(SubjectiveDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        username = self.params['username']
        target_directory = self.params['target_directory']

        BBLogger.log(f"Starting fetch process for SourceForge user '{username}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            BBLogger.log(f"Fetching list of repositories for SourceForge user '{username}'.")
            url = f"https://sourceforge.net/rest/u/{username}/projects/"
            response = requests.get(url)

            if response.status_code != 200:
                error_msg = f"Failed to fetch repositories: HTTP {response.status_code}"
                BBLogger.log(error_msg)
                raise ConnectionError(error_msg)

            repos = response.json()
            if not repos:
                BBLogger.log(f"No repositories found for user '{username}'.")
                return

            BBLogger.log(f"Found {len(repos)} repositories. Starting cloning process.")

            for repo in repos:
                repo_name = repo.get('name', 'Unnamed Repository')
                clone_url = repo.get('git_url')
                if clone_url:
                    self.clone_repo(clone_url, target_directory, repo_name)
                else:
                    BBLogger.log(f"No clone URL found for repository '{repo_name}'. Skipping.")

        except requests.RequestException as e:
            BBLogger.log(f"Error fetching repositories from SourceForge: {e}")
        except Exception as e:
            BBLogger.log(f"Unexpected error: {e}")

    def clone_repo(self, repo_clone_url, target_directory, repo_name):
        try:
            BBLogger.log(f"Cloning repository '{repo_name}' from {repo_clone_url}...")
            subprocess.run(['git', 'clone', repo_clone_url], cwd=target_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log(f"Successfully cloned '{repo_name}'.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error cloning repository '{repo_name}': {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error cloning repository '{repo_name}': {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return the SVG code for the SourceForge icon."""
        return """
<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" fill="#000000">
  <circle cx="512" cy="512" r="512" style="fill: rgb(255, 102, 0);" />
  <path d="M548.2 525.8c0-83.5-29.7-121.5-45.5-135.9-3.1-2.6-7.9-.4-7.4 3.9 3.1 47.2-56.4 59-56.4 132.9v.4c0 45 34.1 81.7 76 81.7s76-36.7 76-81.7v-.4c0-21-7.9-41.1-15.7-55.9-1.7-3.1-4.5-1.7-4.5 3.9z" fill="#fff"/>
</svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for SourceForge.
        """
        return {
            "connection_type": "SourceForge",
            "fields": ["username", "target_directory"]
        }


