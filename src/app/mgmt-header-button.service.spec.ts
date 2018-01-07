import { TestBed, inject } from '@angular/core/testing';

import { MgmtHeaderButtonService } from './mgmt-header-button.service';

describe('MgmtHeaderButtonService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [MgmtHeaderButtonService]
    });
  });

  it('should be created', inject([MgmtHeaderButtonService], (service: MgmtHeaderButtonService) => {
    expect(service).toBeTruthy();
  }));
});
