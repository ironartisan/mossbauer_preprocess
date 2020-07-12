#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : cyl
# @Time : 2020/7/9 21:36
import re

dest_file = './example/1-3/1-3.scf'


def get_lines(scffile_path):
    with open(scffile_path, 'r') as f:
        text =f.readlines()
        return text


def get_Fe_atoms(structfile_path):
    Fe_atoms = []
    for n,line in enumerate(get_lines(structfile_path)):
        line = [i for i in line.split(' ') if i != '']
        if line[0] == "ATOM":
            serial_number = ""
            for i in line[1]:
                if i in "0123456789":
                    serial_number = serial_number + i
            serial_number = int(serial_number)
        if "Fe" in line[0]:
            Fe_atoms.append(serial_number)
    return Fe_atoms


def get_MM(scffile_path, iron_idx):
    MM = []
    pat_MM = re.compile(r':MMI\d{3}:.+?=.*')
    for line in get_lines(scffile_path):
        match_MM = pat_MM.match(line)
        if match_MM:
            match_MM = match_MM.group().split()[-1]
            MM.append(match_MM)
    return MM[: len(iron_idx)]


def get_HFF(scffile_path, iron_idx):
    HFF = []
    pat_HFF = re.compile(r':HFF\d{3}:.*')
    for line in get_lines(scffile_path):
        match_HFF = pat_HFF.match(line)
        if match_HFF:
            match_HFF = match_HFF.group().split()[-2]
            HFF.append(match_HFF)
    return HFF[: len(iron_idx)]


def get_ETA(scffile_path, iron_idx):
    ETA = []
    pat_ETA = re.compile(r':ETA\d{3}:.*')
    for line in get_lines(scffile_path):
        match_ETA = pat_ETA.match(line)
        if match_ETA:
            match_ETA = match_ETA.group().split()[-1]
            ETA.append(match_ETA)
    return ETA[: len(iron_idx)]


def get_EFG(scffile_path, iron_idx):
    EFG = []
    pat_EFG = re.compile(r':EFG\d{3}:.+?=.*')
    for line in get_lines(scffile_path):
        match_EFG = pat_EFG.match(line)
        if match_EFG:
            match_EFG = match_EFG.group().split()[-5]
            EFG.append(match_EFG)
    return EFG[: len(iron_idx)]


def get_RTO(scffile_path, iron_idx):
    RTO = []
    pat_RTO = re.compile(r':RTO\d{3}:.*')
    for line in get_lines(scffile_path):
        match_RTO = pat_RTO.match(line)
        if match_RTO:
            match_RTO = match_RTO.group().split()[-1]
            RTO.append(match_RTO)
    return RTO[: len(iron_idx)]


if __name__ == '__main__':
    value = get_ETA(dest_file, range(1,11))
    for i in value:
        print(i)


