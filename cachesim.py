# -*- coding: utf-8 -*-

class CPU:
    def __init__(self, cache_size = 10, line=10):
        # cria o gerenciador de memoria com os valores recebidos
        self.mmu = MMU(cache_size, line)

    def load_trace(self, trace_location):
        # funcao responsavel por abrir o arquivo de trace
        #  e executar todas as instrucoes
        with open(trace_location, 'r') as trace_file:
            for line in trace_file:
                #[s,l] addr
                ll = line.split()
                operation = ll[0]
                addr = ll[1]
                self.mmu.operate(hex(int(addr, 16)), operation)
        return self.mmu.print_stats()


class MMU:
    def __init__(self, size, line):
        # tamanho da memoria
        self.base = size
        # tamanho da linha
        self.line_size = line
        self.cache = MemoryUnit(self.base, line=self.line_size)

    def print_stats(self):
        # funcao para imprimir os resultados
        # so execute isto depois de terminar a simulacao
        print 'cache'
        print 'hits', self.cache.cache_hits()
        print 'misses', self.cache.cache_misses()
        print 'mma ', self.cache.get_mma()
        return [self.cache.cache_hits(), self.cache.get_mma()]

    def operate(self, addr, operation):
        if operation == 'l':
            self.read_addr(addr)
        if operation == 's':
            self.write_addr(addr)

    def read_addr(self, addr):
        if addr in self.cache:
            return 'hit'
        else:
            self.cache.dict_load(addr)
            return 'miss'

    def write_addr(self, addr):
        if addr in self.cache:
            self.cache.write(addr)
        else:
            self.cache.dict_load(addr)
            self.cache.write(addr)

class MemoryUnit:
    def __init__(self, size, line=1):
        # tamanho da cache
        self.size = size
        # tamanho da linha
        self.line_size = line
        # 1 if valid, 0 otherwise
        self.status = [0] * self.size
        # key -> addr, value -> position
        self.dict_storage = {}
        # lista para controle do LRU
        self.usage_list = [None]*self.size
        # variaveis p/ estatisticas
        self.total_count = 0
        self.hits = 0
        self.misses = 0
        self.mma = 0 #main memory access

    def cache_hits(self):
        # TAXA de acerto
        return  self.hits/float(self.total_count)

    def cache_misses(self):
        # TAXA de erro
        return self.misses/float(self.total_count)

    def get_mma(self):
        # main memory access
        return self.mma

    def make_stats(self, addr):
        self.total_count += 1
        if addr in self.dict_storage:
            self.hits += 1
        else:
            self.misses += 1

    def __contains__(self, item):
        self.make_stats(item)
        if item in self.dict_storage:
            self.usage_list.pop(self.usage_list.index(item))
            self.usage_list.append(item)
            return True
        else:
            return False

    def dict_load(self, addr):
        self.mma += 1
        # tem espaco na memoria
        if len(self.dict_storage) < self.size:
            for i in range(self.line_size):
                if len(self.dict_storage) < self.size:
                    if addr not in self.dict_storage:
                        self.dict_storage[addr] = 1
                        self.usage_list.pop(0) # pop first element
                        self.usage_list.append(addr)
                        addr = hex(int(addr, 16) + 1)
        # nao tem espaco, LRU diz quem deve sair
        else:
            mma_flag = False
            for i in range(self.line_size):
                if addr not in self.dict_storage:
                    r = self.usage_list[0]
                    if self.dict_storage[r] == 2:
                        mma_flag = True
                    self.dict_storage.pop(r, None)
                    self.dict_storage[addr] = 1
                    self.usage_list.pop(0)
                    self.usage_list.append(addr)
                    addr = hex(int(addr, 16) + 1)

    def write(self, addr):
        self.dict_storage[addr] = 2

cache_size = 512
cpu = CPU(cache_size, 16)
filename = 'traces/1.trace'
r = cpu.load_trace(filename)
