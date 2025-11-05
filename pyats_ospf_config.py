from pyats import aetest
import logging

# Set up logging for better visibility during execution
log = logging.getLogger(__name__)

# --- Testscript Definition ---
class OSPF_Integration_Test(aetest.TestScript):
    """
    A pyATS testscript to verify OSPF state and apply new OSPF configuration
    to integrate the router into the company network.
    """

    # --- Common Setup Stage ---
    @aetest.setup
    def common_setup(self, testbed):
        """
        Setup stage: Connect to the device defined in the testbed file.
        The device name 'router1' must match the name in testbed.yaml.
        """
        # Ensure the testbed contains the device alias 'router1'
        if 'router1' not in testbed.devices:
            self.failed('Testbed does not contain device "router1"')

        self.device = testbed.devices['router1']

        log.info(f"Connecting to device: {self.device.alias} ({self.device.connections.cli.ip})")
        try:
            # Establish the connection
            self.device.connect(learn_hostname=True, init_config=False)
            log.info(f"Connection successful. Device hostname: {self.device.hostname}")
        except Exception as e:
            self.failed(f"Failed to connect to device {self.device.alias}: {e}")

    # --- Verification Stage ---
    @aetest.test
    def ShowOspfState(self):
        """
        Task 1: Get and display the current OSPF routing state (neighbors).
        Uses the 'parse' method for structured data retrieval.
        """
        log.info("--- Starting OSPF State Verification ---")
        try:
            # Execute the 'show ip ospf neighbor' command and parse the output
            ospf_output = self.device.parse('show ip ospf neighbor')
            
            # Save the parsed output to the runtime context
            self.passed(f"Successfully retrieved OSPF neighbor state.", ospf_output=ospf_output)

            # Check if any neighbors are found
            if ospf_output.get('neighbors'):
                log.info(f"Current OSPF neighbors found: {len(ospf_output['neighbors'])}")
                for interface, data in ospf_output['neighbors'].items():
                    for neighbor_id, neighbor_data in data['neighbor'].items():
                        log.info(f"  Interface: {interface} | Neighbor ID: {neighbor_id} | State: {neighbor_data['state']}")
            else:
                log.info("No OSPF neighbors currently configured or active.")
                
        except Exception as e:
            self.failed(f"Failed to retrieve or parse OSPF data: {e}")

    # --- Configuration Stage ---
    @aetest.test
    def ConfigureOSPF(self):
        """
        Task 2: Configure the router to join the company's OSPF Area 0.
        Configuration commands are defined here.
        """
        log.info("--- Starting OSPF Configuration ---")

        # Define the configuration block as a multiline string
        # NOTE: Replace '1' with your desired OSPF process ID and 
        # the network/wildcard values with your actual company network range.
        ospf_config = """
        router ospf 1
            network 192.168.10.0 0.0.0.255 area 0
            network 10.0.0.0 0.255.255.255 area 0
            log-adjacency-changes
        """

        log.info(f"Applying configuration:\n{ospf_config.strip()}")

        try:
            # Apply the configuration using the 'configure' method
            output = self.device.configure(ospf_config)
            self.passed("OSPF configuration applied successfully.")
            
            # Optional: Log the output of the configuration attempt
            # log.debug(f"Configuration output: {output}")

        except Exception as e:
            self.errored(f"Failed to apply OSPF configuration: {e}")

    # --- Common Cleanup Stage ---
    @aetest.cleanup
    def common_cleanup(self):
        """
        Cleanup stage: Disconnect from the device.
        """
        log.info("Disconnecting from device.")
        self.device.disconnect()

if __name__ == '__main__':
    # This block allows you to run the script standalone for debugging purposes
    # by simulating a mock testbed loading.
    import argparse
    from pyats.topology import loader

    # Create the argument parser
    parser = argparse.ArgumentParser(description="Standalone PyATS OSPF Script")
    parser.add_argument('--testbed', dest='testbed', type=loader.load, required=True,
                        help='Testbed file path')
    
    args, sys_args = parser.parse_known_args()
    
    aetest.main(testbed=args.testbed, **args.__dict__)
