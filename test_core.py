import os
import pickle
import unittest

from bs4 import BeautifulSoup

from crawler import _build_url, _parse_job_list
from history import load_seen_urls, save_seen_urls


WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))


class CrawlerTests(unittest.TestCase):
    def test_build_url_encodes_keyword_and_page(self):
        url = _build_url("데이터분석", 2)

        self.assertIn("searchword=%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B6%84%EC%84%9D", url)
        self.assertIn("recruitPage=2", url)

    def test_parse_job_list_handles_missing_optional_fields(self):
        html = """
        <div class="item_recruit">
            <div class="job_tit">
                <a href="/zf_user/jobs/relay/view?rec_idx=123">Python 개발자</a>
            </div>
            <div class="corp_name"><a>테스트회사</a></div>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        jobs = _parse_job_list(soup, "python")

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Python 개발자")
        self.assertEqual(jobs[0]["company"], "테스트회사")
        self.assertEqual(jobs[0]["location"], "정보 없음")
        self.assertTrue(jobs[0]["url"].startswith("https://www.saramin.co.kr"))


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(WORKSPACE_DIR, "_test_seen_urls.pkl")
        if os.path.exists(self.path):
            os.remove(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_load_missing_history_returns_empty_set(self):
        self.assertEqual(load_seen_urls(self.path), set())

    def test_save_and_load_history_roundtrip(self):
        seen = {"https://example.com/a", "https://example.com/b"}

        save_seen_urls(seen, self.path)

        self.assertEqual(load_seen_urls(self.path), seen)

    def test_invalid_history_type_returns_empty_set(self):
        with open(self.path, "wb") as f:
            pickle.dump(["not", "a", "set"], f)

        loaded = load_seen_urls(self.path)

        self.assertEqual(loaded, set())


if __name__ == "__main__":
    unittest.main()
