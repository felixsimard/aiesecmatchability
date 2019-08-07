set :branch, :master
set :deploy_to, '/root/matchability_api'
server "159.89.115.87", user: "root", roles: %w(app db)