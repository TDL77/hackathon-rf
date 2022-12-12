# Всероссийский хакатон 2022
## Системы мониторинга и оперативного уведомления

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