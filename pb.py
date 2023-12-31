from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.models.consumer.v3.channel import Channel
from pubnub.models.consumer.v3.uuid import UUID

from .config import config

cipher_key = config.get("pubnub_cipher_key")
pn_config = PNConfiguration()
pn_config.publish_key = config.get("pubnub_publish_key")
pn_config.subscribe_key = config.get("pubnub_subscribe_key")
pn_config.uuid = config.get("pubnub_uuid")
pn_config.secret_key = config.get("pubnub_secret_key")
#pn_config.cipher_key = cipher_key
pubnub = PubNub(pn_config)


def grant_read_access(user_id):
    channels = [
            Channel.id(config.get("pubnub_channel")).read()
            ]
    uuids = [
            UUID.id("uuid-d").get().update()
            ]
    envelope = pubnub.grant_token().channels(channels).ttl(15).uuids(uuids).authorized_uuid(user_id).sync()
    return envelope.result.token


def grant_read_write_access(user_id):
    channels = [
            Channel.id(config.get("pubnub_channel")).read().write()
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
    read_access= token_details['resources']['channels']['johns_sd3b_pi']['read']
    write_access= token_details['resources']['channels']['johns_sd3b_pi']['write']
    uuid = token_details['authorized_uuid']

    return token_details['timestamp'], token_details['ttl'], uuid, read_access, write_access


