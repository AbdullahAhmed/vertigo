"""Generate private deployment configuration once. Output stays in ignored build/deploy."""
from pathlib import Path
import json, secrets, subprocess, sys
root=Path(__file__).resolve().parents[1]
out=root/'build/deploy/analytics-secrets';out.mkdir(parents=True,exist_ok=True)
if (out/'config.php').exists():
    print('Keeping existing analytics credentials:',out/'admin-access.txt');sys.exit(0)
php=sys.argv[1] if len(sys.argv)>1 else 'php'
password=secrets.token_urlsafe(24)
hashed=subprocess.check_output([php,'-r','$p=stream_get_contents(STDIN); echo password_hash($p,PASSWORD_BCRYPT);'],input=password.encode()).decode()
secret=secrets.token_hex(32)
config="<?php\nreturn [\n'password_hash'=>'"+hashed+"',\n'secret'=>'"+secret+"',\n'origin'=>getenv('VERTIGO_ANALYTICS_ORIGIN') ?: 'https://vertigo.alphasquaredgames.com',\n'data_dir'=>getenv('VERTIGO_ANALYTICS_DATA') ?: dirname(__DIR__,3).'/.vertigo-analytics',\n];\n"
(out/'config.php').write_text(config,encoding='utf8')
(out/'credentials.json').write_text(json.dumps({'password':password}),encoding='utf8')
(out/'admin-access.txt').write_text('VERTIGO private analytics\n\nDashboard: https://vertigo.alphasquaredgames.com/analytics/\nPassword: '+password+'\n\nKeep this file private. Do not commit it or include it in a deployment ZIP.\nThe password protects analytics only; the game remains public.\n',encoding='utf8')
print('Private credentials saved:',out/'admin-access.txt')
