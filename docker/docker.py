import logging
from docker import Client

log = logging.getLogger(__name__)

class ContainerDataCollector(object):

	  # @stats[:cpu_percent] += calculate_cpu_percent(container_id, stats["cpu_stats"]["cpu_usage"]["total_usage"], s
	   #    tats["cpu_stats"]["system_cpu_usage"], stats["cpu_stats"]["cpu_usage"]["percpu_usage"].count)
		

		 #  def calculate_cpu_percent(container_id, total_container_cpu, total_system_cpu, num_processors)
	  #   # The CPU values returned by the docker api are cumulative for the life of the process, which is not what we want.
	  #   now = Time.now
	  #   last_cpu_stats = memory(container_id)
	  #   if @last_run && last_cpu_stats
	  #     container_cpu_delta = total_container_cpu - last_cpu_stats[:container_cpu]
	  #     system_cpu_delta = total_system_cpu - last_cpu_stats[:system_cpu]
	  #     cpu_percent = cpu_percent(container_cpu_delta, system_cpu_delta, num_processors)
	  #   end
	  #   remember(container_id => {:container_cpu => total_container_cpu, :system_cpu => total_system_cpu})
	  #   return cpu_percent || 0
	  # end
	def calculate_cpu_percent(self, prev_cpu, current_cpu):
		cpu_percent = float(0)

		num_processors = len(current_cpu["cpu_usage"]['percpu_usage'])
		

		container_cpu_delta = current_cpu["cpu_usage"]['total_usage']-prev_cpu["cpu_usage"]['total_usage']
		system_cpu_delta = current_cpu['system_cpu_usage']-prev_cpu['system_cpu_usage']


		if container_cpu_delta > 0 and system_cpu_delta > 0:
			cpu_percent = (container_cpu_delta / system_cpu_delta) * num_processors * 100.0

		return cpu_percent

	def container_processes(self, container_id):
		result = {}
		container_top =  self.client.top(container_id)

		container_processes = container_top.get('Processes')
		header = container_top.get('Titles')

		if container_processes and header:
			header = [x.lower() for x in header]
			result = {'header': header, 'data': container_processes}

		return result


	def collect_container_data(self, container):
		container_id = container.get('Id')
		total_loops = 0
		
		try:
			name = container.get('Names')[0].strip("/")
		except:
			name = ""

		result = {
			"created": container.get('Created'),
			"container_id": container_id,
			"name": name,
			"image": container.get('Image'),
			"status": container.get('Status'),
			"processes": self.container_processes(container_id)
		}

		


		 # @stats[:cpu_percent] += calculate_cpu_percent(container_id, stats["cpu_stats"]["cpu_usage"]["total_usage"], s
   #    tats["cpu_stats"]["system_cpu_usage"], stats["cpu_stats"]["cpu_usage"]["percpu_usage"].count)
   #    @stats[:memory_usage] += stats["memory_stats"]["usage"].to_f / 1024.0 / 1024.0
   #    @stats[:memory_limit] += stats["memory_stats"]["limit"].to_f / 1024.0 / 1024.0
   #    @stats[:network_in] += stats["network"]["rx_bytes"].to_f / 1024.0
   #    @stats[:network_out] += stats["network"]["tx_bytes"].to_f / 1024.0
		prev_cpu = {}
		for i in self.client.stats(container_id, True):
			if total_loops == 0:
				# Remember CPU
				prev_cpu = i['cpu_stats']

			if total_loops == 1:
				result['network_out'] = i['network']['tx_bytes'] / 1024
				result['network_in'] = i['network']['rx_bytes'] / 1024
				result['memory'] = i['memory_stats']['usage'] / 1024 / 1024
				result['memory_limit'] = i['memory_stats']['limit'] / 1024 / 1024
				result['cpu_percent'] = self.calculate_cpu_percent(prev_cpu, i['cpu_stats'])
				return result
			elif total_loops == 2:
				break

			total_loops = total_loops+1


		return result


	def collect(self):
		result = []
		try:
			self.client = Client(base_url='unix://var/run/docker.sock', version='1.17')
		except:
			log.exception('Unable to connect to the Docker API.')
			self.client = False

		if self.client:

			try:
				running_containers = self.client.containers(filters={'status': 'running'})
			except:
				running_containers = []

			procs = []
			total_running_containers = len(running_containers)
			if total_running_containers > 0:

				# Wait for Docker to release an update with all the containers data collected in one go, until then: 
				for container in running_containers:
					p = self.collect_container_data(container)
					result.append(p)
					
		return result
				



container_data_collector = ContainerDataCollector()