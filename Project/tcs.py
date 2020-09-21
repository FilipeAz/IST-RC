import sys
import socket

if len(sys.argv) == 1:
	TCSport = 58048

else: 
	TCSport = int(sys.argv[2])

TCSname = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((TCSname, TCSport))
languages_list = [] 
# languages_list elements have the format [language_name, (ip, port)]


while True:
	message, addr = sock.recvfrom(2100)
	messages = message.split()


	# User-TCS (UDP)

	if messages[0] == 'ULQ' and len(messages) != 1:
		answer = 'ULR ERR\n' # wrong request
		sock.sendto(answer, addr)
	

	elif messages[0] == 'ULQ' and len(messages) == 1:
		lang_count = len(languages_list)
		
		if lang_count == 0:
			answer = 'ULR EOF\n' # no languages available
			sock.sendto(answer, addr)
		
		if lang_count != 0: # sends list of available languages
			answer = 'ULR ' + str(lang_count)
			languages = ''
			for i in languages_list:
				answer += ' ' + i[0] 
				languages += i[0] + ' '
			answer += '\n'
			sock.sendto(answer, addr)
			print 'List request: ' + socket.gethostbyname(addr[0]) + ' ' + str(addr[1]) + '\n ' + languages
	

	elif messages[0] == 'UNQ':
		
		if len(messages) == 2:
			requested_language = messages[1]
			answer = ''

			for i in languages_list:
				if requested_language == i[0]:
					IPTRS = i[1][0]
					portTRS = i[1][1]
					answer = 'UNR ' + str(IPTRS) + ' ' + str(portTRS) + '\n'
					sock.sendto(answer, addr)
					print IPTRS + ' ' + str(portTRS)

			if answer == '':
				answer = 'UNR EOF\n' # language not found
				sock.sendto(answer, addr)

			
		else:
			answer = 'UNR ERR\n' # more than one language requested
			sock.sendto(answer, addr)




	# TRS-TCS (UDP)

	elif messages[0] == 'SRG': # adding a new TRS
		if len(messages) == 4:
			language = messages[1]
			IPTRS = messages[2]
			portTRS = messages[3]

			answer = ''
			
			for i in languages_list:
				if i[0] == language: # language already has a dedicated trs 
					answer = 'SRG NOK\n'
					sock.sendto(answer, addr)
					break

			if answer == '': # otherwise, add to list
				languages_list.append([language,(IPTRS,portTRS)])
				answer = 'SRG OK\n'
				sock.sendto(answer, addr)
				print '+' + language + ' ' + IPTRS + ' ' + str(portTRS)
				
		else: # wrong syntax
			answer = 'SRR ERR\n'
			sock.sendto(answer, addr)

	
	elif messages[0] == 'SUN': # closing the TRS
		if len(messages) == 4:
			language = messages[1]
			IPTRS = messages[2]
			portTRS = messages[3]
			answer = ''
			for i in languages_list:
				if i[0] == language and i[1][0] == IPTRS and i[1][1] == portTRS:
					languages_list.remove(i)
					answer = 'SUR OK\n'
					sock.sendto(answer, addr)
					print '-' + language + ' ' + IPTRS + ' ' + str(portTRS)
			if answer == '':
				answer = 'SUR NOK\n'
				sock.sendto(answer, addr)
				print '-' + language + ' ' + IPTRS + ' ' + str(portTRS)
			
		else: # wrong syntax
			answer = 'SUR ERR\n'
			sock.sendto(answer, addr)
			
			
			
			
		
		






