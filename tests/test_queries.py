import datetime
import unittest

from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from fastcore.basics import AttrDict

from github_collector import models, queries


class TestQueries(unittest.TestCase):
    def test_add_pulls(self):
        session = UnifiedAlchemyMagicMock()

        queries.add_pulls(session, [
            AttrDict(
                id=570341824,
                owner="numpy",
                repository="numpy",
                number=18377,
                title="ENH: Add annotations for `np.lib.ufunclike`",
                user=AttrDict(
                    id="43369155"
                ),
                state="closed",
                created_at="2021-02-09T14:28:20Z",
                updated_at="2021-02-09T20:06:10Z",
                closed_at=None,
                merged_at=None
            )
        ], "numpy", "numpy")

        pr = session.query(models.PullRequest).one()
        assert (pr.id == 570341824)
        assert (pr.owner == "numpy")
        assert (pr.repository == "numpy")
        assert (pr.number == 18377)
        assert (pr.title == "ENH: Add annotations for `np.lib.ufunclike`")
        assert (pr.user_id == "43369155")
        assert (pr.state == "closed")
        assert (pr.created_at == datetime.datetime(2021, 2, 9, 14, 28, 20))
        assert (pr.updated_at == datetime.datetime(2021, 2, 9, 20, 6, 10))
        assert (pr.closed_at is None)
        assert (pr.merged_at is None)

    def test_add_files(self):
        session = UnifiedAlchemyMagicMock()

        queries.add_files(session,
                          AttrDict(
                              id=570341824
                          ),
                          [
                              AttrDict(
                                  filename="numpy/__init__.pyi",
                                  status="modified",
                                  additions=6,
                                  deletions=3,
                                  changes=9
                              )
                          ]
                          )

        file = session.query(models.PullRequestFile).one()
        assert (file.pr_id == 570341824)
        assert (file.filename == "numpy/__init__.pyi")
        assert (file.status == "modified")
        assert (file.additions == 6)
        assert (file.deletions == 3)
        assert (file.changes == 9)


if __name__ == '__main__':
    unittest.main()
