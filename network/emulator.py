
import subprocess

PARTIES = 3
SUBNET = "10.10.0"
BRIDGE = "mpc-br"

class NetworkEmulator:
    def __init__(self, parties=3, subnet="10.10.0"):
        self.parties = parties
        self.subnet = subnet
        self.bridge = "mpc-br"

    def run(self, *args):
        "Execute linux cmd"
        subprocess.run(args, check= True)


    def create_namespace(self, party):
        "create isolated network for a party"

        name = f"mpc{party}"

        self.run("ip", "netns", "add", name)
        self.run("ip", "netns", "exec", name, "ip", "link", "set", "lo", "up")
        
    def create_bridge(self):
        "create a virtual switch between alll parties"
        self.run("ip", "link", "add", self.bridge, "type", "bridge")
        self.run("ip", "link", "set", self.bridge, "up")

    def connect_party(self, party):
        "Connect a party's namespace to the Bridge"

        name = f"mpc{party}"
        veth = f"veth{party}"
        ip_address = f"{self.subnet}.{10 + party}/24"

        #Create two connected virtual Eth ints''
        self.run("ip", "link", "add", veth, "type", "veth",
            "peer", "name", f"peer{party}")


         # Move one interface into the party's namespace
        self.run("ip", "link", "set", f"peer{party}", "netns", name)

        # Connect the other interface to the bridge
        self.run("ip", "link", "set", veth, "master", self.bridge)
        self.run("ip", "link", "set", veth, "up")

        # Configure the interface inside the namespace
        self.run("ip", "netns", "exec", name,
            "ip", "link", "set", f"peer{party}", "name", "eth0")

        self.run("ip", "netns", "exec", name,
            "ip", "addr", "add", ip_address, "dev", "eth0")

        self.run("ip", "netns", "exec", name,
            "ip", "link", "set", "eth0", "up")

    def setup(self):
        "Creat ethe complete virtual MPC network"
        self.create_bridge()

        for party in range(self.parties):
            self.create_namespace(party)
            self.connect_party(party)

        print("MPC network created succesfully")


    def configure(self, party, latency=0, bandwidth=1000, jitter =0, loss=0):
        "configure network conditions for one party"

        if not 0 <= party < self.parties:
            raise ValueError("invalid party id")

        if latency < 0 or jitter < 0 or bandwidth <= 0 or not 0 <= loss <=100:
            raise ValueError("invalid network parameters")

        name = f"mpc{party}"

        self.run(
            "ip", "netns", "exec", name,
            "tc", "qdisc", "replace",
            "dev", "eth0",
            "root", "netem",
            "delay", f"{latency}ms", f"{jitter}ms",
            "loss", f"{loss}%",
            "rate", f"{bandwidth}mbit"
        )


        print(f"Network conditions configured for Party {party}.")

    def status(self):
        "display the network conditions for every Party"

        for party in range(self.parties):
            print(f"\nParty {party}:")

            self.run(
                "ip", "netns", "exec", f"mpc{party}",
                "tc", "qdisc", "show", "dev", "eth0"
            )

    def reset(self):
        "Remove artificial network restrictions"

        for party in range(self.parties):
             subprocess.run(
                [
                    "ip", "netns", "exec", f"mpc{party}",
                    "tc", "qdisc", "del", "dev", "eth0", "root"
                ],
                check=False
            )

    def teardown(self):
        for party in range(self.parties):
            subprocess.run(
                ["ip", "netns", "del", f"mpc{party}"],
                check=False
            )

        subprocess.run(
            ["ip", "link", "del", self.bridge],
            check=False
        )

        print("MPC network removed.")
