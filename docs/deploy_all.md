## how to deploy all my homelab sersices 

### my python bot for lenses
#### this python bot counts 15 days, and texts to me, when i need to change my lenses

1. create namespace
kubectl create namespace bots

2. create secret with tg token
kubectl -n bots create secret generic lenses-bot-secret \
  --from-literal=TELEGRAM_BOT_TOKEN=UR_TOKEN

3. apply manifest
kubectl apply -f lenses.yaml -n bots