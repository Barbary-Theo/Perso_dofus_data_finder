from requester import Requester


def main():
    requester = Requester()
    resources, consommables, apparats, status = requester.update_dofus()

    print(f"Synchronization finally terminated, resources collected : {len(resources)}, consommables collected : {len(consommables)}, apparats collected : {len(apparats)}")


if __name__ == "__main__":
    main()
