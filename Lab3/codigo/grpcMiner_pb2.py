# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: grpcMiner.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fgrpcMiner.proto\x12\x04main\"\x1b\n\tintResult\x12\x0e\n\x06result\x18\x01 \x01(\x05\"C\n\x0cstructResult\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x10\n\x08solution\x18\x02 \x01(\t\x12\x11\n\tchallenge\x18\x03 \x01(\x05\"\x15\n\x06result\x12\x0b\n\x03num\x18\x01 \x01(\x05\"&\n\x04\x61rgs\x12\x0e\n\x06numOne\x18\x01 \x01(\x05\x12\x0e\n\x06numTwo\x18\x02 \x01(\x05\"&\n\rtransactionId\x12\x15\n\rtransactionId\x18\x01 \x01(\x05\"J\n\rchallengeArgs\x12\x15\n\rtransactionId\x18\x01 \x01(\x05\x12\x10\n\x08\x63lientId\x18\x02 \x01(\x05\x12\x10\n\x08solution\x18\x03 \x01(\t\"\x06\n\x04void2\xef\x02\n\x03\x61pi\x12\x1f\n\x03\x61\x64\x64\x12\n.main.args\x1a\x0c.main.result\x12/\n\x10getTransactionId\x12\n.main.void\x1a\x0f.main.intResult\x12\x34\n\x0cgetChallenge\x12\x13.main.transactionId\x1a\x0f.main.intResult\x12<\n\x14getTransactionStatus\x12\x13.main.transactionId\x1a\x0f.main.intResult\x12\x37\n\x0fsubmitChallenge\x12\x13.main.challengeArgs\x1a\x0f.main.intResult\x12\x31\n\tgetWinner\x12\x13.main.transactionId\x1a\x0f.main.intResult\x12\x36\n\x0bgetSolution\x12\x13.main.transactionId\x1a\x12.main.structResultb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'grpcMiner_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _INTRESULT._serialized_start=25
  _INTRESULT._serialized_end=52
  _STRUCTRESULT._serialized_start=54
  _STRUCTRESULT._serialized_end=121
  _RESULT._serialized_start=123
  _RESULT._serialized_end=144
  _ARGS._serialized_start=146
  _ARGS._serialized_end=184
  _TRANSACTIONID._serialized_start=186
  _TRANSACTIONID._serialized_end=224
  _CHALLENGEARGS._serialized_start=226
  _CHALLENGEARGS._serialized_end=300
  _VOID._serialized_start=302
  _VOID._serialized_end=308
  _API._serialized_start=311
  _API._serialized_end=678
# @@protoc_insertion_point(module_scope)
