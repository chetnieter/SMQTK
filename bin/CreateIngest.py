#!/usr/bin/env python
"""
Create an ingest of files in a specified directory.
"""

import glob
import logging
import os.path as osp

from SMQTK.utils import bin_utils
from SMQTK.utils.configuration import IngestConfiguration


def main():
    usage = "%prog [options] GLOB [ GLOB [ ... ] ]"
    description = "Create a formal ingest from a set of file paths or " \
                  "shell-style glob strings."

    parser = bin_utils.SMQTKOptParser(usage, description=description)
    parser.add_option('-i', '--ingest',
                      help="Configured ingest to 'ingest' into.")
    parser.add_option('-l', '--list-ingests', action='store_true',
                      default=False,
                      help="List available ingests we can ingest new data "
                           "into. See the system_config.json file in the etc "
                           "directory for more details.")
    parser.add_option('-v', '--verbose', action='store_true', default=False,
                      help='Add debug messaged to output logging.')
    opts, args = parser.parse_args()

    bin_utils.initializeLogging(logging.getLogger(),
                                logging.INFO - (10*opts.verbose))
    log = logging.getLogger("main")

    if opts.list_ingests:
        log.info("")
        log.info("Available Ingests:")
        for k in sorted(IngestConfiguration.available_ingest_labels()):
            log.info("\t%s", k)
        log.info("")
        exit(0)

    if opts.ingest is None:
        log.info("")
        log.info("ERROR: Please provide an ingest label.")
        log.info("")
        exit(1)

    ingest_config = IngestConfiguration(opts.ingest)
    ingest = ingest_config.new_ingest_instance()
    log.debug("Script arguments:\n%s" % args)
    for g in args:
        g = osp.expanduser(g)
        if osp.isfile(g):
            ingest.add_data_file(g)
        else:
            log.debug("Expanding glob: %s" % g)
            for fp in glob.glob(g):
                ingest.add_data_file(fp)


if __name__ == '__main__':
    main()
