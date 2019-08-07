set :application, 'matchability_api'
set :repo_url, 'https://github.com/aiesecinternational/matchability'
set :git_http_username, 'alisoliman'
ask :git_http_password
set :deploy_via, :remote_cache
set :scm, :git
set :stages, ["staging", "production"]
set :default_stage, "staging"
set :keep_releases, 3


namespace :deploy do
     desc 'Create virtualenv'
     task :create_virtual_env do
          on roles(:app, :db) do
               within release_path do
                    execute "cd #{release_path}; virtualenv -p python3 matchability_api/env"
               end
          end
     end
     desc 'Install requirements'
     task :install_requirements do
          on roles(:app, :db) do
               within release_path do
                    execute "cd #{release_path}; source matchability_api/env/bin/activate; pip install --upgrade pip"
                    execute "cd #{release_path}; source matchability_api/env/bin/activate; pip install -r matchability_api/requirements.txt"

               end
          end
     end
     desc 'Install UWSGI'
     task :install_uwsgi do
          on roles(:app) do
               within release_path do
                    execute "cd #{release_path}; source matchability_api/env/bin/activate; pip install uwsgi"
               end
          end
     end
     desc 'stop uwsgi'
     task :stop_uwsgi do
          on roles(:app) do
               within release_path do
                    execute "cd #{release_path}; source matchability_api/env/bin/activate; uwsgi --stop /tmp/matchability_api-master-uwsgi.pid || true"
               end
          end
     end
     desc 'Run migrations'
     task :run_migrations do
          on roles(:db) do
               within release_path do
                    execute "cd #{release_path}; source matchability_api/env/bin/activate; ./matchability_api/manage.py migrate"
               end
          end
     end
     desc 'Start uwsgi'
     task :start_uwsgi do
          on roles(:app) do
               within release_path do
                    execute "cd #{release_path}; source matchability_api/env/bin/activate; uwsgi --module core.wsgi --http-socket 127.0.0.1:5000 --master --processes 2 --daemonize /var/log/uwsgi/matchability_api.log --pidfile /tmp/matchability_api-master-uwsgi.pid"
               end
          end
     end
     after :updated, :create_virtual_env
     after :updated, :install_requirements
     after :updated, :install_uwsgi
     after :updated, :stop_uwsgi
     after :updated, :run_migrations
     after :updated, :start_uwsgi
end