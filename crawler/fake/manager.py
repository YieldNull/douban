from crawler.fake import USER_AGENTS, rand_cookie
import random

FAKE_META_NAME = 'fake_pair'


class FakePair(object):
    counter = 0

    def __init__(self, agent, cookie):
        FakePair.counter += 1
        self.pid = FakePair.counter

        self.agent = agent
        self.cookie = cookie

    def __str__(self):
        return 'Cookie:{:s} UA:{:s}'.format(self.cookie, self.agent)


pool = []

for agent in USER_AGENTS:
    pool.append(FakePair(agent=agent, cookie=rand_cookie()))
    pool.append(FakePair(agent=agent, cookie=rand_cookie()))


def peek_fake_pair():
    return random.choice(pool)


def pop_fake_pair(fake_pair: FakePair):
    pool.remove(fake_pair)
    pool.append(FakePair(fake_pair.agent, rand_cookie()))
