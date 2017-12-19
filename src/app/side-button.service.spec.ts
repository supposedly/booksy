import { TestBed, inject } from '@angular/core/testing';

import { SideButtonsService } from './side-buttons.service';

describe('SideButtonsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [SideButtonsService]
    });
  });

  it('should be created', inject([SideButtonsService], (service: SideButtonsService) => {
    expect(service).toBeTruthy();
  }));
});
