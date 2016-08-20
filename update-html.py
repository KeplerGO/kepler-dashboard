import json
import dateutil.parser
from jinja2 import Environment, FileSystemLoader

metrics = json.load(open('kepler-dashboard.json'))
month = dateutil.parser.parse(metrics['last_update']).strftime('%B %Y')

j2_env = Environment(loader=FileSystemLoader('html/'),
                     trim_blocks=True)
tmpl = j2_env.get_template('dashboard-template.html')
output_fn = 'html/index.html'
print('Writing {}'.format(output_fn))
with open(output_fn, 'w') as output:
    output.write(tmpl.render(metrics=metrics, month=month))
