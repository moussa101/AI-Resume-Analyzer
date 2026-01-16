
import {
    Controller,
    Post,
    UseInterceptors,
    UploadedFile,
    UseGuards,
    Request,
    Get,
    Param,
    ParseIntPipe,
    Body,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { ResumesService } from './resumes.service';
import { multerOptions } from './multer.config';
import { ApiTags, ApiOperation, ApiConsumes, ApiBody, ApiBearerAuth } from '@nestjs/swagger';
import { AuthGuard } from '@nestjs/passport';
import { MlService } from './ml.service';

@ApiTags('resumes')
@ApiBearerAuth()
@Controller('resumes')
@UseGuards(AuthGuard('jwt'))
export class ResumesController {
    constructor(
        private readonly resumesService: ResumesService,
        private readonly mlService: MlService,
    ) { }

    @Post()
    @ApiOperation({ summary: 'Upload a resume file' })
    @ApiConsumes('multipart/form-data')
    @ApiBody({
        schema: {
            type: 'object',
            properties: {
                file: {
                    type: 'string',
                    format: 'binary',
                },
            },
        },
    })
    @UseInterceptors(FileInterceptor('file', multerOptions))
    async uploadFile(@UploadedFile() file: Express.Multer.File, @Request() req) {
        const resume = await this.resumesService.create({
            filePath: file.path,
            fileName: file.originalname,
            fileSize: file.size,
            user: { connect: { id: req.user.id } },
        });

        return {
            message: 'File uploaded successfully',
            resume,
        };
    }

    @Post(':id/analyze')
    @ApiOperation({ summary: 'Analyze a resume against a job description' })
    @ApiBody({
        schema: {
            type: 'object',
            properties: {
                jobDescription: { type: 'string', description: 'Job description text' },
            },
            required: ['jobDescription'],
        },
    })
    async analyzeResume(
        @Param('id', ParseIntPipe) id: number,
        @Body() body: { jobDescription: string },
    ) {
        const resume = await this.resumesService.findOne(id);
        if (!resume) {
            return { error: 'Resume not found' };
        }

        const analysis = await this.mlService.analyzeResume(resume.filePath, body.jobDescription);

        // Save analysis to DB
        const savedAnalysis = await this.resumesService.createAnalysis({
            matchScore: analysis.score,
            skillsFound: analysis.skills_found,
            missingSkills: analysis.missing_keywords,
            jobDescText: body.jobDescription,
            feedback: analysis.feedback,
            resume: { connect: { id } },
        });

        return {
            analysis: savedAnalysis,
            details: analysis,
        };
    }

    @Get()
    @ApiOperation({ summary: 'Get all resumes for the current user' })
    async findAll(@Request() req) {
        return this.resumesService.findAll(req.user.id);
    }

    @Get(':id')
    @ApiOperation({ summary: 'Get a specific resume' })
    async findOne(@Param('id', ParseIntPipe) id: number) {
        return this.resumesService.findOne(id);
    }
}

