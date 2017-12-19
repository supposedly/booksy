import { TestBed, inject } from '@angular/core/testing';

import { CurrentMediaSessionService } from './current-media-session.service';

describe('CurrentMediaSessionService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [CurrentMediaSessionService]
    });
  });

  it('should be created', inject([CurrentMediaSessionService], (service: CurrentMediaSessionService) => {
    expect(service).toBeTruthy();
  }));
});
