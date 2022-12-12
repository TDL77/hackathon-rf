# Всероссийский хакатон 2022
## Системы мониторинга и оперативного уведомления

### Постановка задачи
Для оперативного уведомления мастера смены обогатительной фабрики об автоматической остановке питающего конвейера в связи со срабатыванием датчика обнаружения посторонних металлических предметов (металлосигнализатор), которые могут вывести из строя дробильное оборудование, необходимо разработать прототип системы мониторинга оборудования и учета простоев. При реализации необходимо предусмотреть возможность классификации причин остановки конвейера (ложное срабатывание металлосигнализатора/авария/обнаружен посторонний предмет) и вывод сводного отчета по простоям на рабочее место диспетчера.

### Модели детекции
Подготовили код и провели эксперименты по детекции для следующих алгоритмов:
- Hotelling's T-squared statistics;
- Hotelling's T-squared statistics + Q statistics based on PCA;
- Isolation forest;
- LSTM-based NN (LSTM);
- Feed-Forward Autoencoder;
- LSTM Autoencoder (LSTM-AE);
- LSTM Variational Autoencoder (LSTM-VAE);
- Convolutional Autoencoder (Conv-AE);
- Multi-Scale Convolutional Recurrent Encoder-Decoder (MSCRED);
- Multivariate State Estimation Technique (MSET).

### Модели классификации
Разработаны модели классификации на основе TSFresh, SKLearn и методов классификации на основе градиентного бустинга. Также подготовили код для ансамблирования алгоритмов.

### Модели оптимизации
Возможно решение задачи создания рекомендаций на основе оптимизации. Подробнее можно ознакомиться в [этом репозитории](https://github.com/waico/evraz-hack).

### Обучение модели
В ходе проведение экспериментов и обучения модели необходимо оборачивать код в контекст экспериментов MLFlow с включенным автоматическим логгироваем. Артефакты обучения применяются в микросервисе применения модели [MLFlowKafkaPredictor](https://github.com/waico/hackathon-rf/tree/main/mlflow-kafka):

```python
import mlflow

mlflow.autolog()
with mlflow.start_run():
    ...

```

### Запуск необходимых сервисов в кластере Kubernates

Устанавливаем strimzi операторы kafka:
```
helm upgrade --install kafka-release strimzi/strimzi-kafka-operator --namespace kafka --create-namespace
```

Устанавливаем артефакты:
```
kubectl apply -f kafka_cluster.yaml -n kafka
kubectl apply -f kafka_user.yaml -n kafka
```

Сгенерируем сертификат и получим пароль пользователя Kafka:
```
kubectl get secret my-user -o jsonpath='{.data.password}' -n kafka | base64 --decode
kubectl get secret my-cluster-cluster-ca-cert -o jsonpath='{.data.ca\.crt}' -n kafka | base64 -d > ca.crt
```

Проверьте доступ до сервера с помощтю утилы `kafkacat`:
```
kcat -L -b bootstrap.192.168.15.160.nip.io:443 -X security.protocol=SASL_SSL -X ssl.ca.location="ca.crt" -X sasl.mechanisms=SCRAM-SHA-512 -X sasl.username="my-user" -X sasl.password="password"
```

Активируйте Kafka-Connect:
```
kubectl apply -f kafka_connect.yaml -n kafka
````

Внесите изменения в конфигурации подключения к СУБД PostgreSQL в файле `debezium.yaml` и активируйте сбор данных из kafka в Debezium:
```
kubectl apply -f debezium.yaml -n kafka
```

### Запуск обученной модели машинного обучения

Произведите запуск микросервиса применения модели [MLFlowKafkaPredictor](https://github.com/waico/hackathon-rf/tree/main/mlflow-kafka) в соответсвии с интрукцией.