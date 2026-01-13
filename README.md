# Notes App

## Обзор
Приложение для управления заметками с аутентификацией, категориями и системой обмена заметками.

## Устранение ошибки обновления StatefulSet

Если вы сталкиваетесь с ошибкой при обновлении Helm-релиза:
```
Error: UPGRADE FAILED: cannot patch "notes-app-postgresql" with kind StatefulSet: StatefulSet.apps "notes-app-postgresql" is invalid: spec: Forbidden: updates to statefulset spec for fields other than 'replicas', 'ordinals', 'template', 'updateStrategy', 'revisionHistoryLimit', 'persistentVolumeClaimRetentionPolicy' and 'minReadySeconds' are forbidden
```

Используйте безопасный скрипт обновления:
```bash
./scripts/helm-upgrade-safe.sh <название-релиза> charts/notes-app <namespace>
```

Или выполните обновление с флагом --force (только если данные не критичны):
```bash
helm upgrade <название-релиза> charts/notes-app --namespace <namespace> --atomic=false --force
```