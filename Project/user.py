import sys
import socket
import os

TCSname = socket.gethostname()
TCSport = 58048

for i in range(1, len(sys.argv), 2):
		if sys.argv[i] == "-p":
			TCSport = int(sys.argv[i+1])
			continue
		elif sys.argv[i] == "-n":
			TCSname = sys.argv[i+1]
			continue


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

languages_list = []


while True:
	# terminal awaiting commands
	sys.stdout.write('> ')
	sys.stdout.flush()
	user_command = raw_input()
	
	#case list
	if user_command == 'list':
		
		sock.sendto('ULQ\n', (TCSname, TCSport))
		message, addr = sock.recvfrom(2100)
		messages = message.split()
		
		if messages[0] == 'ULR':

			if messages[1] != 'EOF' and messages[1] != 'ERR':
				languages_nr = int(messages[1])
				messages = messages[2:]
				a = 1
				s = ''
				languages_list = []
				
				for i in messages:
					languages_list.append(str(i))
					s = str(a) + '- ' + str(i)
					a += 1
					print s
			elif messages[1] == 'EOF':
				print 'Nao existem linguagens disponiveis.'
			
			elif messages[1] == 'ERR':
				print 'O pedido ULQ nao foi bem formulado.'
				
		else:
			print 'O TCS nao seguiu o protocolo esperado.'
		
	#case exit
	elif user_command == 'exit':
		sock.close()
		sys.exit()
		
	#case request translation
	elif languages_list != []:
		requests = user_command.split()

		if requests[0] == 'request':

			lang_id = int(requests[1])
			language_request = 'UNQ ' + languages_list[lang_id - 1] + '\n' # requests translation to TCS
			sock.sendto(language_request, (TCSname, TCSport))
			
			message, addr = sock.recvfrom(2100)
			answer = message.split()

			if answer[0] == 'UNR':

				if answer[1] != 'EOF' or answer[1] != 'ERR':
					# connects to TRS returned by TCS
					IPTRS = answer[1]
					portTRS = int(answer[2])
					s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s_tcp.connect((IPTRS, portTRS))
					
					trad = 'TRQ '

					# textual translation
					if requests[2] == 't':
						requests = requests[3:]
						trad += 't ' + str(len(requests)) 

						for i in requests:
							trad += ' ' + i
						trad += '\n'
						s_tcp.send(trad) # requests translation to TRS
						
						resposta = s_tcp.recv(2100)
						resposta = resposta.split()

						print str(IPTRS) + ' ' + str(portTRS)

						if resposta[1]== 'NTA':
							print 'Pelo menos uma das palavras que solicitou nao tem traducao no servidor.'

						if resposta[1] == 'ERR':
							print 'Pedido mal formulado.'
				
						else: # prints formatted translation
							resposta = resposta[3:]
							for i in resposta:
								print '\t' + str(IPTRS) + ': ' + i

					#image translation
					elif requests[2] == 'f':
						filename = requests[3]
					
						trad += 'f ' + filename + ' '
					
						f = open(filename, 'rb')


						size =  int(os.path.getsize(filename)) # file size
						tamanho = str(size)
						trad += tamanho + ' '
						dat = f.read(size)
					
						trad += dat + '\n'
						print '\t' + tamanho + ' Bytes to transmit.'

						s_tcp.send(trad)
						
						an = ''
						space_count = 0
						while space_count != 4:
							l = s_tcp.recv(1) # receives single byte

							if space_count == 1 and (l == 'N' or l == 'E'):
							   break # error case, jumps to else

							if l == ' ':
								space_count = space_count + 1

							an = an + l

						if space_count != 1: # writing image to disk
							res = an.split()
							size = int(res[-1])
							image = open(res[2], 'wb')
							k = ''
							while (len(k) < size):
								k += s_tcp.recv(1)								
							image.write(k)
							image.close()

							print 'received file ' + filename + '\n' + '\t' + res[3] + ' Bytes'
						

						else: # error cases
							if l == 'N':
								print 'Nao existe traducao para a imagem pedida.'
							if l == 'E':
								print 'Pedido mal formulado.'

						s_tcp.close()
						
						
				elif answer[1] == 'EOF':
					print 'O pedido UNQ nao pode ser respondido.'
					
				elif answer[1] == 'ERR':
					print 'O pedido UNQ nao estava bem formulado.'
				
				else:
					print 'O TCS nao seguiu o protocolo esperado.'
					
			else:
				print 'O TCS nao seguiu o protocolo esperado.'

	elif languages_list == [] and request[0] == 'request':
		print 'Por favor, escreva list para saber quais as linguagens disponiveis'
		
	else:
		print 'Comando nao suportado.'

	
