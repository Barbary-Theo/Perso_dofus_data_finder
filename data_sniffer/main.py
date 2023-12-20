import io
import binascii
import threading

import pyshark

from data import Buffer, Data


def packet_handler(pkt):

    if hasattr(pkt, 'data'):

        buffer = Buffer()
        buffer += bytes.fromhex(pkt.data.data)

        packet_id, len_data, content = deserialize_header(buffer)

        if packet_id is not None:
            message = deserialize_packet_content(buffer, packet_id, content)

            if message is not None:
                print(message)

        buffer.end()


def deserialize_header(buffer):

    try:
        header = buffer.readUnsignedShort()
        len_data = int.from_bytes(buffer.read(header & 3), "big")
        packet_id = header >> 2
        content = Data(buffer.read(len_data))
        return [packet_id, len_data, content]
    except IndexError:
        buffer.pos = 0
        print("Unable to parse the header : Not complete")
        return [None, None, None]


def deserialize_packet_content(buffer: Buffer, packet_id, content: Data):
    message = {}

    try:
        if packet_id == 9240:

            message["object_GID"] = content.readVarUhInt()
            message["object_type"] = content.readInt()
            item_type_description_len = content.readUnsignedShort()

            item_type_description = []
            for i in range(item_type_description_len):
                item_type_description_object = {}
                item_type_description_object["object_UID"] = content.readVarUhInt()
                item_type_description_object["object_GID"] = content.readVarUhInt()
                item_type_description_object["object_type"] = content.readInt()

                effects_len = content.readUnsignedShort()
                effects = []
                for j in range(effects_len):
                    effects_object = {}
                    effects_object["id4"] = content.readUnsignedShort()
                    effects_object["action_id"] = content.readUnsignedShort()
                    effects.append(effects_object)
                item_type_description_object["effects"] = effects

                prices_len = content.readUnsignedShort()
                if prices_len > 3:
                    prices_len = content.readVarUhShort()

                prices_object = {}
                prices_object["price_no"] = prices_len

                for j in range(prices_object["price_no"]):
                    prices_object[str(j)] = content.readVarUhLong()

                item_type_description_object["prices"] = prices_object

                item_type_description.append(item_type_description_object)

            message["item_type_description"] = item_type_description
            return message

    except IndexError:
        print(f"Unable to parse this packet with id {packet_id} : {message}")
        buffer.pos = 0
        return None

    return None


def main():
    capture = pyshark.LiveCapture(interface='Ethernet 5', display_filter='tcp.port == 5555')
    capture.apply_on_packets(packet_handler)


if __name__ == "__main__":
    main()
