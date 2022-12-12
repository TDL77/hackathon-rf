import logging
import json
import os
import pandas as pd
import mlflow

from confluent_kafka import Consumer, Producer


class KafkaPredictor:

    def __init__(self, model_s3_path) -> None:
        self.model = mlflow.pyfunc.load_model(model_s3_path, dst_path='model')

    def run(self) -> None:

        conf = {
            'bootstrap.servers': os.environ.get('KAFKA_HOST'),
            'group.id': "prediction",
            'auto.offset.reset': 'smallest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['data'])

        producer = Producer({'bootstrap.servers': os.environ.get('KAFKA_HOST')})

        minutes_offset = int(os.environ.get('MINUTES_OFFSET'))
        
        logging.info(f'Minutes offset: {minutes_offset}')

        result_df = pd.DataFrame()

        try:
            logging.info("Start pooling")
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg:
                    if msg.error():
                        logging.error("Consumer error: {}".format(msg.error()))
                    else:
                        message_value = msg.value().decode('utf-8')
                        message_json = json.loads(message_value)
                        
                        input_df = pd.DataFrame(message_json)\
                            .pivot(index="Timestamp", columns="ItemId", values='Value')\
                            .reset_index()\
                            .rename_axis(None, axis=1)\
                            .fillna(method='ffill')
                        input_df['Timestamp'] = pd.to_datetime(input_df['Timestamp'])
                        input_df.set_index('Timestamp', inplace=True)

                        result_df = pd.concat([result_df, input_df])
                        min_df = result_df.resample('min').mean()
                        if len(min_df) < minutes_offset:
                            continue

                        min_df = min_df.tail(minutes_offset).fillna(method='ffill').fillna(method='bfill')

                        try:
                            input_df = min_df.astype("float32")
                            prediction_df = self.model.predict(input_df)
                        except Exception as e:
                            logging.error(e)
                            continue

                        message = prediction_df.to_json()
                        producer.produce("predict", json.dumps(message))
                        producer.flush()

                        logging.info(message)

        except KeyboardInterrupt as e:
            logging.info("Stoping Kafka inferece.")
        except Exception as e:
            logging.error(e)
        finally:
            consumer.close()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Initialize predictor with model from S3.
    model_s3_path = os.environ.get('S3_MODEL')
    predictor = KafkaPredictor(model_s3_path)

    # Run predictor
    predictor.run()
