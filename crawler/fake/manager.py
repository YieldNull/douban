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


class FakeManager(object):
    def __init__(self):
        self.pool = []

        self.continuous_forbid_count = 0
        self.forbid_threshold = 10

        for agent in USER_AGENTS:
            self.pool.append(FakePair(agent=agent, cookie=rand_cookie()))
            self.pool.append(FakePair(agent=agent, cookie=rand_cookie()))

    def peek_fake_pair(self):
        return random.choice(self.pool)

    def pop_fake_pair(self, fake_pair: FakePair):

        if fake_pair in self.pool:  # 有可能多个403Request使用同一个fake_pair,已经被移除
            self.pool.remove(fake_pair)
            self.pool.append(FakePair(fake_pair.agent, rand_cookie()))
            self.continuous_forbid_count += 1

        return self.continuous_forbid_count >= self.forbid_threshold

    def succeed_fake_pair(self, fake_pair: FakePair):
        self.continuous_forbid_count = 0
