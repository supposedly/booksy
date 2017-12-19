import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { NavButton, httpOptions } from './exports';
import { LoggingService } from './logging.service';

@Injectable()
export class MediaService {

  constructor() { }

}
