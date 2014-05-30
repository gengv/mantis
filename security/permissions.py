# coding: utf-8
from flask_principal import RoleNeed, Permission

normal_user_role = RoleNeed(1)

normal_user_permission = Permission(normal_user_role)