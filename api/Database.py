import os
from dotenv import load_dotenv
from django.http import JsonResponse, Http404
import psycopg2
from psycopg2.extras import RealDictCursor


class Database:
	connection = None
	cursor = None

	def query(self, query_str):
		load_dotenv()
		try:
			self.cursor = self.connect()
			self.cursor.execute(query_str)

			records = self.cursor.fetchall()
			rowcount = self.cursor.rowcount
			self.connection.commit()
			# print(f"Found {rowcount} rows")
			self.disconnect()
			return {'records': records, 'count': rowcount}
		except (Exception, psycopg2.DatabaseError) as error:
			self.disconnect()
			print(error)
			return JsonResponse({'error': str(error)}, content_type="application/json")

	def connect(self):
		if self.connection is None:
			try:
				self.connection = psycopg2.connect(database=os.environ.get("DB_NAME"),
												   user=os.environ.get("DB_USERNAME"),
												   password=os.environ.get("DB_PASS"),
												   host=os.environ.get("DB_HOST"),
												   port=os.environ.get("DB_PORT"),
												   cursor_factory=RealDictCursor)
				return self.connection.cursor()
			except Exception as error:
				JsonResponse({'error': str(error)})

	def disconnect(self):
		if self.cursor is not None:
			self.cursor.close()
			self.cursor = None
			# print("Closing cursor")

		if self.connection is not None:
			self.connection.close()
			self.connection = None
			# print("Closing connection")

	def does_patient_exist(self, patient_id):
		number_of_rows_found = self.query(f"SELECT * FROM KNOAP.patient WHERE id = {patient_id};")['count']
		# print(f"NO OF RO {number_of_rows_found}")
		return number_of_rows_found == 1

	def insert_new_patient_diagnosis(self, patient_id, prediction, confidence, index):
		query = """INSERT INTO KNOAP.diagnosis (patient_id, prediction, confidence, index)
				   VALUES ('%s', '%s', %d, %d) RETURNING *;""" % (patient_id, prediction, confidence, index)
		result = self.query(query)
<<<<<<< HEAD
		print(f"DIAGNOSIS ADDED {result['records']}")
		return result['records'][0]

	def get_patient_by_id(self, id):
		records = self.query(f"SELECT * FROM KNOAP.patient WHERE id = {id};")
		if (records['count'] == 0):
			raise Http404

		return records['records']

	def get_patient_diagnosis(self, patient_id):
		records = self.query(f"SELECT * FROM KNOAP.diagnosis WHERE patient_id = {patient_id};")['records']
		dictionary = []
		for key in records:
			dictionary.append(dict(key))
		return dictionary
=======
		return result['records'][0]
>>>>>>> 4d20f221ecd5a78f3bc079644513837a21183408
