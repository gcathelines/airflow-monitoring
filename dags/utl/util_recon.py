# Copyright (c) PT Pintu Kemana Saja 2024 All Rights Reserved.

from prometheus_client import (CollectorRegistry, Gauge,
                               push_to_gateway)

import pandas as pd
import numpy as np
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


class UtilRecon:
    registry = CollectorRegistry()
    pushgateway_url = 'localhost:9091'
    _recon_summary_metrics = Gauge(
        name='order_recon_summary',
        documentation='Run Duration of a DAG',
        labelnames=['vendor', 'pair', 'type', 'unit'],
        registry=registry
    )

    @staticmethod
    def send_recon_summary_metrics(vendor, df: pd.DataFrame):
        recon_results = df.copy()

        for i, row in recon_results.iterrows():
            unit_string = row["pair"].split("_")[0]
            UtilRecon._recon_summary_metrics.labels(
                vendor=vendor,
                pair=row['pair'],
                type="accumulated_base_discrepancy",
                unit=unit_string
            ).set(row['accumulated_base_discrepancy'])

            UtilRecon._recon_summary_metrics.labels(
                vendor=vendor,
                pair=row['pair'],
                type="mirrored_buy",
                unit="IDR"
            ).set(row['mirrored_buy'])

            UtilRecon._recon_summary_metrics.labels(
                vendor=vendor,
                pair=row['pair'],
                type="mirrored_sell",
                unit="IDR"
            ).set(row['mirrored_sell'])

            UtilRecon._recon_summary_metrics.labels(
                vendor=vendor,
                pair=row['pair'],
                type="unmirrored_buy",
                unit="IDR"
            ).set(row['unmirrored_buy'])

            UtilRecon._recon_summary_metrics.labels(
                vendor=vendor,
                pair=row['pair'],
                type="unmirrored_sell",
                unit="IDR"
            ).set(row['unmirrored_sell'])

            UtilRecon._recon_summary_metrics.labels(
                vendor=vendor,
                pair=row['pair'],
                type="price",
                unit="IDR"
            ).set(row['price'])

            if not np.isnan(row['pending_internal_data_count']):
                UtilRecon._recon_summary_metrics.labels(
                    vendor=vendor,
                    pair=row['pair'],
                    type="pending_internal_data_count",
                    unit=""
                ).set(row['pending_internal_data_count'])

            if not np.isnan(row['pending_external_data_count']):
                UtilRecon._recon_summary_metrics.labels(
                    vendor=vendor,
                    pair=row['pair'],
                    type="pending_external_data_count",
                    unit=""
                ).set(row['pending_external_data_count'])

        try:
            push_to_gateway(
                gateway=UtilRecon.pushgateway_url,
                job=vendor,
                grouping_key={'vendor': vendor},
                registry=UtilRecon.registry,
            )
        except Exception as e:
            logging.error(
                f"Failed to push metrics for vendor {vendor}: {e}"
            )
