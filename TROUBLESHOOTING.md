# Устранение неполадок при установке и обновлении Notes App

## Ошибка обновления StatefulSet PostgreSQL

**Проблема**: 
```
Error: UPGRADE FAILED: cannot patch "notes-app-postgresql" with kind StatefulSet: StatefulSet.apps "notes-app-postgresql" is invalid: spec: Forbidden: updates to statefulset spec for fields other than 'replicas', 'ordinals', 'template', 'updateStrategy', 'revisionHistoryLimit', 'persistentVolumeClaimRetentionPolicy' and 'minReadySeconds' are forbidden
```

**Причина**:
Kubernetes не позволяет изменять определенные поля в спецификации StatefulSet после его создания. Это особенно часто происходит при обновлении Helm-чартов, где изменяются запрещенные поля.

**Решения**:

### 1. Использование безопасного скрипта обновления (рекомендуется)

```bash
./scripts/helm-upgrade-safe.sh <название-релиза> charts/notes-app <namespace>
```

Этот скрипт автоматически обрабатывает потенциальные конфликты при обновлении.

### 2. Обновление с флагом --force

```bash
helm upgrade <название-релиза> charts/notes-app --namespace <namespace> --atomic=false --force
```

> **Важно**: Используйте этот метод только если данные в базе не являются критичными или если была создана резервная копия.

### 3. Ручное удаление StatefulSet (крайняя мера)

> ⚠️ **Предупреждение**: Этот метод может привести к потере данных. Обязательно создайте резервную копию перед выполнением.

```bash
# Создайте резервную копию данных (если необходимо)
kubectl exec -it <release-name>-postgresql-0 -n <namespace> -- pg_dump -U postgres -d notesdb > backup.sql

# Удалите StatefulSet (без каскадного удаления, чтобы сохранить PVC)
kubectl delete statefulset <release-name>-postgresql -n <namespace> --cascade=false

# Повторите команду обновления Helm
helm upgrade <название-релиза> charts/notes-app --namespace <namespace>
```

### 4. Уменьшение до 0 реплик и обратно

```bash
# Уменьшите количество реплик до 0
kubectl scale statefulset <release-name>-postgresql -n <namespace> --replicas=0

# Подождите, пока все поды завершатся
kubectl wait --for=delete pod/<release-name>-postgresql-0 -n <namespace>

# Выполните обновление Helm
helm upgrade <название-релиза> charts/notes-app --namespace <namespace>
```

## Дополнительные рекомендации

### Проверка состояния ресурсов

```bash
# Проверьте статус всех ресурсов
kubectl get all -n <namespace>

# Проверьте статус StatefulSet
kubectl get statefulsets -n <namespace>

# Подробная информация о StatefulSet
kubectl describe statefulset <release-name>-postgresql -n <namespace>
```

### Проверка логов

```bash
# Логи PostgreSQL пода
kubectl logs <release-name>-postgresql-0 -n <namespace>

# Логи обновления Helm
helm history <название-релиза> -n <namespace>
```

### Восстановление из резервной копии

Если вы случайно потеряли данные, вы можете восстановить их из резервной копии:

```bash
kubectl exec -it <release-name>-postgresql-0 -n <namespace> -- psql -U postgres -d notesdb -f /path/to/backup.sql
```

## Профилактика

1. Всегда создавайте резервные копии перед обновлениями
2. Используйте безопасный скрипт обновления
3. Тестируйте обновления в тестовой среде перед применением в продакшене
4. Проверяйте совместимость версий компонентов перед обновлением