#
# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
#

import rocks.commands

class Plugin(rocks.commands.Plugin):

	def provides(self):
		return 'MAPREDUCE2'

	def clientComponents(self):
		return ['MAPREDUCE2_CLIENT']
