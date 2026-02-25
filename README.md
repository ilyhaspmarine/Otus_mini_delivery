### ПОДГОТОВКА
#### в /etc/hosts прописываем
```
127.0.0.1 arch.homework 
```

#### Запускаем docker
любым вариантом, у меня docker desktop с виртуализацией VT-d

#### Запускаем minikube
```
minikube start --driver=docker
```

#### NGINX
Считам, что с прошлых дз он всё ещё в кластере


### СТАВИМ ПРИЛОЖЕНИЕ
#### Создаем namespace под сервис аутентификации
```
kubectl create namespace delivery
```

#### "Внешняя" поставка секретов в кластер
##### Секрет с данными для подключения к БД
```
kubectl apply -f ./secret/delivery_secret.yaml -n delivery
```

#### Переходим в директорию с чартом
```
cd ./delivery
```

#### Загружаем чарты зависимостей
```
helm dependency update
```

#### Возвращаемся в корень
```
cd ../
```

#### Устанавливаем чарт сервиса
```
helm install delivery delivery -n delivery
```

#### Включаем (и не закрываем терминал)
```
minikube tunnel
```

#### Проверяем health-check (в новом окне терминала)
```
curl http://arch.homework/delivery/health/
```


### КАК УДАЛИТЬ ПРИЛОЖЕНИЕ
#### Удаляем чарт и БД
```
helm uninstall delivery -n delivery
```

#### Удаляем секрет
```
kubectl delete secret delivery-db-secret -n delivery
```

#### Удаляем PVC, оставшиеся от БД
```
kubectl delete pvc -l app.kubernetes.io/name=delivery-postgresql,app.kubernetes.io/instance=delivery -n delivery
```

#### Сносим PV, оставшиеся от БД (если reclaimPolicy: Retain)
```
kubectl get pv -n delivery
```
Смотрим вывод, узнаем <имя PV> (к сожалению, меток у него не будет - я проверил)
```
kubectl delete pv <имя PV> -n delivery
```

### Готово!