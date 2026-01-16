
import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { ResumesService } from './resumes.service';
import { ResumesController } from './resumes.controller';
import { PrismaService } from '../prisma.service';
import { MlService } from './ml.service';

@Module({
    imports: [HttpModule],
    controllers: [ResumesController],
    providers: [ResumesService, PrismaService, MlService],
})
export class ResumesModule { }

