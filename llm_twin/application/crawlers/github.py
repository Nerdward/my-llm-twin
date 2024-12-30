import os
import shutil
import subprocess
import tempfile

from aws_lambda_powertools import Logger

from llm_twin.domain.documents import RepositoryDocument

from .base import BaseCrawler

logger = Logger(service="nnaemeka/crawler")


class GithubCrawler(BaseCrawler):
    model = RepositoryDocument

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")) -> None:
        super().__init__()
        self._ignore = ignore

    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Repository already exists in the database: {link}")

            return

        logger.info(f"Starting scrapping Github repository: {link}")

        repo_name = link.rstrip("/").split("/")[-1]

        local_temp = tempfile.mkdtemp()

        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])

            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree = {}
            for root, dirs, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue

                for file in files:
                    if file.endswith(self._ignore):
                        continue

                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "")
            user = kwargs["user"]
            instance = self.model(
                name=repo_name,
                link=link,
                content=tree,
                author_id=user.id,
                author_full_name=user.full_name,
            )

            instance.save()

        except Exception:
            raise

        finally:
            shutil.rmtree(local_temp)

        logger.info(f"Finished scrapping Github repository: {link}")
