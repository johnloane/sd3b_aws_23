from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.models.consumer.v3.channel import Channel
from pubnub.models.consumer.v3.uuid import UUID


cipher_key = 'secret123!'
pn_config = PNConfiguration()
pn_config.publish_key = "pub-c-6ce775ac-3b15-47e0-937b-e5bd7cf6c79d"
pn_config.subscribe_key = "sub-c-6eb23377-44fd-4c6e-b456-974c422b6cc7"
pn_config.uuid = "115286914554441662160"
pn_config.secret_key = "sec-c-YzE0ODlhZTQtNjkzOS00ZDYyLWIxNjAtMTk1NjcwOWY5NGY4"
#pn_config.cipher_key = cipher_key
pubnub = PubNub(pn_config)


def grant_read_access(user_id):
    channels = [
            Channel.id("johns_sd3b_pi").read()
            ]
    uuids = [
            UUID.id("uuid-d").get().update()
            ]
    envelope = pubnub.grant_token().channels(channels).ttl(15).uuids(uuids).authorized_uuid(user_id).sync()
    return envelope.result.token


def grant_read_write_access(user_id):
    channels = [
            Channel.id("johns_sd3b_pi").read().write()
            ]
    uuids = [
            UUID.id("uuid-d").get().update()
            ]
    envelope = pubnub.grant_token().channels(channels).ttl(15).uuids(uuids).authorized_uuid(user_id).sync()
    return envelope.result.token

def revoke_access(token):
    envelope = pubnub.revoke_token(token).sync()


def parse_token(token):
    token_details = pubnub.parse_token(token)
    print(token_details)
    return token_details['timestamp'], token_details['ttl']



