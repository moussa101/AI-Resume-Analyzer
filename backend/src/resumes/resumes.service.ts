
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { Prisma } from '@prisma/client';

@Injectable()
export class ResumesService {
    constructor(private prisma: PrismaService) { }

    async create(data: Prisma.ResumeCreateInput) {
        return this.prisma.resume.create({
            data,
        });
    }

    async findAll(userId: number) {
        return this.prisma.resume.findMany({
            where: { userId },
            orderBy: { createdAt: 'desc' },
            include: { analyses: true },
        });
    }

    async findOne(id: number) {
        return this.prisma.resume.findUnique({
            where: { id },
            include: { analyses: true },
        });
    }

    async createAnalysis(data: Prisma.AnalysisCreateInput) {
        return this.prisma.analysis.create({
            data,
        });
    }
}

