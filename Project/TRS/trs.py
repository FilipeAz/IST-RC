import sys, socket, os, signal


#./TRS language
language = sys.argv[1]
TRSport = 59000
TCSname = socket.gethostname()
TCSport = 58048
	
# reading arguments
for i in range(2, len(sys.argv), 2):
	if sys.argv[i] == '-p':
		TRSport = int(sys.argv[i+1])
		continue
	elif sys.argv[i] == '-n':
		TCSname = sys.argv[i+1]
		continue
	elif sys.argv[i] == '-e':
		TCSport = sys.argv[i+1]
		continue

def translator(connection,address):

	request = connection.recv(5)
	lrequest = request.split()
	name = socket.gethostbyaddr(address[0])
	string_print = name[0] + ' ' + str(address[1]) + ': '
	# file translation
	if lrequest[1] == 'f' and lrequest[0] == 'TRQ':
		space_count = 0

		while True:
			l = connection.recv(1)
							
			if l == ' ':
				space_count += 1
							
			request += l
							
			if space_count == 3:
				break
		

		
		message = request.split()
		filename = message[2]
		size = message[3]
		img = open(filename, 'wb')
		
		img_data = ''

		while (len(img_data) < int(size)):
			img_data += connection.recv(1)								
		img.write(img_data)
		
		
			
		f_filename = language + '_file_translation.txt'
		flist = open(f_filename,'r');
		answer = 'TRR f '
			
		translated_file = ''
			
		while flist != 'EOF':
			line = flist.readline()
			line = line.split()
			if line[0] == filename: 
				answer += line[1] + ' '
				translated_file = line[1]
				break

		if flist == 'EOF': # translated file not found
			answer = 'TRR NTA'
			return answer
				


		f = open(line[1], 'rb') 
		size =  int(os.path.getsize(line[1])) # file size
		size_str = str(size)
		answer += size_str + ' '
		
		data = f.read()
		print size_str
		
		answer += data + '\n'
		img.close()
		flist.close()
		f.close()
	
		print string_print + filename + '\n' + size + 'Bytes received' + '\n' + translated_file + '(' + size_str + ')'
	
		return answer




	
	# text translation
	elif lrequest[1] == 't' and lrequest[0] == 'TRQ':
		request += connection.recv(2100)
		message = request.split()
		
		word_count = message[2]
		message = message[3:]

		answer = 'TRR t ' + str(word_count) + ' '
		filename = language + '_text_translation.txt'
		translation_file = open(filename, 'r') # opens translation file
			
		words_to_translate = ''
		translated_words = ''
		for w in message:
			words_to_translate += w + ' ' 
			while translation_file != 'EOF':
				line = translation_file.readline()
				line = line.split()

				if translation_file == 'EOF' or line == []: # error case, word not found
					answer = 'TRR NTA\n'
					translation_file.close()
					return answer

				if line[0] == w: 
					answer += line[1] + ' '
					translated_words += line[1] + ' '
					break


			translation_file.seek(0, 0) # sets file pointer to beggining of file	
			
		answer += '\n'
		translation_file.close()
		print string_print + words_to_translate + '\n' + translated_words + '(' + word_count + ')'
		return answer




	# error cases
	else:
		answer = 'TRR ERR\n'
		return answer




			
try:
	# TRS-TCS (UDP)

	s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
	s_udp.connect((TCSname, TCSport)) # connection to TCS

	# TRS registers on TCS
	answer = 'SRG ' + language + ' ' + str(socket.gethostbyname(socket.gethostname())) + ' ' + str(TRSport)
	s_udp.sendto(answer, (TCSname, TCSport))

	message, addr = s_udp.recvfrom(2100)
	messages = message.split() # gets answer from TCS
	
	if messages[0] == 'SRR':
		if messages[1] == 'NOK' or messages[1] == 'ERR':
			print 'Registo negado'
			sys.exit(0)


	# USER-TRS (TCP)

	s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
	s_tcp.bind((socket.gethostname(), TRSport))
	s_tcp.listen(5) # waits for users

	
	while True:
		connection, address = s_tcp.accept()
		answer = translator(connection,address) # calls function
		connection.sendall(answer)
		connection.close()
		
		
	


except KeyboardInterrupt: # Deals with Ctrl+c
	answer = 'SUN ' + language + ' ' + socket.gethostbyname(socket.gethostname()) + ' ' + str(TRSport)
	s_udp.sendto(answer, (TCSname, TCSport))
	message, addr = s_udp.recvfrom(2100)
	messages = message.split()

	if messages[0] == 'SUR':
		if messages[1] == 'NOK' or messages[1] == 'ERR':
			print 'TCS nao deixa acabar'
		if messages[1] == 'OK':
			s_tcp.close()
			s_udp.close()
			print '\nexit'
			sys.exit(0)



			
	
	
 
